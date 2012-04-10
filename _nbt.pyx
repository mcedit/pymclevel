# cython: profile=True
# vim:set sw=2 sts=2 ts=2:

"""
Cython implementation

Named Binary Tag library. Serializes and deserializes TAG_* objects
to and from binary data. Load a Minecraft level by calling nbt.load().
Create your own TAG_* objects and set their values.    
Save a TAG_* object to a file or StringIO object.

Read the test functions at the end of the file to get started.

This library requires Numpy.    Get it here:
http://new.scipy.org/download.html

Official NBT documentation is here:
http://www.minecraft.net/docs/NBT.txt


Copyright 2010 David Rio Vierra
"""

import collections
import itertools
import struct
import gzip
from cStringIO import StringIO
from cpython cimport PyTypeObject, PyObject_TypeCheck, PyUnicode_DecodeUTF8, PyList_Append

cdef extern from "cStringIO.h":
    struct PycStringIO_CAPI:
        int cwrite (object o, char *buf, Py_ssize_t len)
        PyTypeObject * OutputType
cdef extern from "cobject.h":
    void * PyCObject_Import(char *module_name, char *cobject_name)

cdef PycStringIO_CAPI *PycStringIO = <PycStringIO_CAPI *>PyCObject_Import("cStringIO", "cStringIO_CAPI")
cdef PyTypeObject * StringO = PycStringIO.OutputType

cdef cwrite(obj, char * buf, size_t len):
    #print "cwrite %s %s %d" % (map(ord, buf[:min(4, len)]), buf[:min(4, len)].decode('ascii', 'replace'), len)
    return PycStringIO.cwrite(obj, buf, len)
    
import sys
import os
from os.path import exists
from contextlib import closing

from numpy import array, zeros, uint8, fromstring, ndarray, frombuffer
cimport numpy as np

cdef char TAG_END = 0
cdef char TAG_BYTE = 1
cdef char TAG_SHORT = 2
cdef char TAG_INT = 3
cdef char TAG_LONG = 4
cdef char TAG_FLOAT = 5
cdef char TAG_DOUBLE = 6
cdef char TAG_BYTE_ARRAY = 7
cdef char TAG_STRING = 8
cdef char TAG_LIST = 9
cdef char TAG_COMPOUND = 10
cdef char TAG_INT_ARRAY = 11
#cdef char TAG_SHORT_ARRAY = 12

class NBTFormatError (ValueError): 
    pass
    
cdef class TAG_Value:
    cdef unicode _name
    cdef public char tagID
    def __str__(self):
        return self.tostr()
    cdef tostr(self):
        return str(self.__class__) + ": " + str(self.value)

        
    property name:
        def __get__(self):
            return self._name
        def __set__(self, val):
            if isinstance(val, str): val = PyUnicode_DecodeUTF8(val, len(val), "strict")
            self._name = val
    
    def __reduce__(self):
        return self.__class__, (self.value, self._name)
        
cdef class TAG_Number(TAG_Value):
    pass
    
cdef class TAG_Array(TAG_Value):
    pass
    
    
cdef class TAG_Byte(TAG_Number):
    cdef public char value
    
    cdef save_value(self, buf):
        save_byte(self.value, buf)
    def __init__(self, char value=0, name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_BYTE
    
cdef class TAG_Short(TAG_Number):
    cdef public short value
    
    cdef save_value(self, buf):
        save_short(self.value, buf)
    def __init__(self, short value=0, name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_SHORT
    
cdef class TAG_Int(TAG_Number):
    cdef public int value

    cdef save_value(self, buf):
        save_int(self.value, buf)
    def __init__(self, int value=0, name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_INT
    
cdef class TAG_Long(TAG_Number):
    cdef public long long value
 
    cdef save_value(self, buf):
        save_long(self.value, buf)
    def __init__(self, long long value=0, name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_LONG
    
cdef class TAG_Float(TAG_Number):
    cdef public float value
    
    cdef save_value(self, buf):
        save_float(self.value, buf)
    def __init__(self, float value=0., name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_FLOAT
    
cdef class TAG_Double(TAG_Number):
    cdef public double value
    
    cdef save_value(self, buf):
        save_double(self.value, buf)
    def __init__(self, double value=0., name = u""): 
        self.value = value
        self.name = name    
        self.tagID = TAG_DOUBLE
    
cdef class TAG_Byte_Array(TAG_Array):
    cdef public object value
    def __init__(self, value = zeros((0,), 'uint8'), name = u""): 
        self.value = value
        self.name = name
        self.tagID = TAG_BYTE_ARRAY
        
    cdef save_value(self, buf):
        save_byte_array(self.value, buf)

cdef class TAG_Int_Array(TAG_Array):
    cdef char _tagID(self): return  TAG_INT_ARRAY
    cdef public object value

    def __init__(self, value = zeros((0,), 'uint32'), name = u""):
        self.value = value
        self.name = name
        self.tagID = TAG_INT_ARRAY

    cdef save_value(self, buf):
        save_int_array(self.value, buf)
    
cdef class TAG_String(TAG_Value):
    cdef unicode _value
    def __init__(self, value = u"", name = u""): 
        if isinstance(value, str): value = PyUnicode_DecodeUTF8(value, len(value), "strict")
        self.value = value
        self.name = name
        self.tagID = TAG_STRING
        
    property value:
        def __get__(self):
            return self._value
        def __set__(self, value):
            if isinstance(value, str): value = PyUnicode_DecodeUTF8(value, len(value), "strict")
            self._value = value
    
    cdef save_value(self, buf):
        save_string(self.value.encode('utf-8'), buf)
        
    
cdef class _TAG_List(TAG_Value):
    cdef public list value
    def __init__(self, value = None, name = u""): 
        self.value = list(value or [])
        self.name = name
        self.tagID = TAG_LIST
        
    """collection methods"""     
    def __getitem__(self, key):
        return self.value[key]
    def __setitem__(self, key, val):
        self.value[key] = val
    def __iter__(self): 
        return iter(self.value)
    def __len__(self): return len(self.value)
    def insert(self, idx, key):
        self.value.insert(idx, key)
    property list_type:
        def __get__(self):
            if len(self.value): return self.value[0].tagID
            return TAG_BYTE
        
    cdef save_value(self, buf):
        save_tag_id(self.list_type, buf)
        save_int(len(self.value), buf)
        
        items = self.value
        for subtag in items:
            if subtag.tagID != self.list_type:
                raise NBTFormatError, "Asked to save TAG_List with different types! Found %s and %s" % (subtag.tagID, self.list_type)
            save_tag_value(subtag, buf)
            
class TAG_List(_TAG_List, collections.MutableSequence):
    pass
            
cdef class _TAG_Compound(TAG_Value):
    cdef public dict value
    def __init__(self, value = None, name = u""): 
        self.value = value or {}
        self.name = name    
        self.tagID = TAG_COMPOUND
          
    """collection methods"""  
    def __getitem__(self, key):
        return self.value[key]
    def __setitem__(self, key, val):
        assert isinstance(val, TAG_Value)
        val.name = key
        self.value[key] = val
    def __delitem__(self, key):
        del self.value[key]
    def __iter__(self): return iter(self.value)
    def __contains__(self, k):return k in self.value
    def __len__(self): return len(self.value)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.value)
    __repr__ = __str__
    def add(self, tag):
        assert tag.name
        self[tag.name] = tag
        
    cdef save_value(self, buf):
        i = self.iteritems()
        for name, subtag in i:
            #print "save_tag_name", name, subtag.tagID, "Named", subtag.name,
            save_tag_id(subtag.tagID, buf)
            #print "id",
            save_tag_name(subtag, buf)
            #print "name",
            save_tag_value(subtag, buf)
            #print "value", name
        save_tag_id(TAG_END, buf)
        
class TAG_Compound(_TAG_Compound, collections.MutableMapping):
    def __init__(self, value = None, name = u""): 
        _TAG_Compound.__init__(self, value, name)
    def save(self, filename = "", buf = None):
        save_root_tag(self, filename, buf)
    def saveGzipped(self, filename, compresslevel=1):
        save_root_tag(self, filename)



#cdef int needswap = (sys.byteorder == "little")
cdef swab(void * vbuf, int nbytes):
    cdef unsigned char * buf = <unsigned char *> vbuf
    #print "Swapping ", nbytes, "bytes"
    #for i in range(nbytes): print buf[i],
    #print "to", 
    #if not needswap: return
    cdef int i
    for i in range((nbytes+1)/2):
        buf[i], buf[nbytes-i-1] = buf[nbytes-i-1], buf[i]
    #for i in range(nbytes): print buf[i],

import zlib
def gunzip(data):
    #strip off the header and use negative WBITS to tell zlib there's no header
    return zlib.decompress(data[10:], -zlib.MAX_WBITS)
def try_gunzip(data):
    try:
        data = gunzip(data)
    except Exception, e:
        pass
    return data
    
def load(buf=None, filename=None):
    try:
        if isinstance(buf, basestring) and exists(buf):
            filename = buf
    except TypeError:
        pass
        
    if filename and exists(filename):
        data = file(filename, "rb").read()
        data = try_gunzip(data)
        return load_buffer(data)
    
    return load_buffer(try_gunzip(buf))

cdef class load_ctx:
    cdef size_t offset
    cdef char * buffer
    cdef size_t size
    cdef int require(self, size_t s) except -1:
        #print "Asked for ", s
        if s > self.size - self.offset:
            raise NBTFormatError, "NBT Stream too short. Asked for %d, only had %d" % (s, (self.size - self.offset))
            
        return 0
        
should_dump = False
cdef load_buffer(bytes buf):
    cdef load_ctx ctx = load_ctx()
    ctx.offset = 1
    ctx.buffer = buf
    ctx.size = len(buf)
    if len(buf) < 1: 
        raise NBTFormatError, "NBT Stream too short!"
    
    if should_dump: print dump(buf)
    assert ctx.buffer[0] == TAG_COMPOUND, "Data is not a TAG_Compound (found %d)" % ctx.buffer[0]
    name = load_string(ctx)
    #print "Root name", name
    tag = load_compound(ctx)
    tag.name = name
    return tag

cdef load_byte(load_ctx ctx):
    ctx.require(1)
    cdef char * ptr = <char *>(ctx.buffer + ctx.offset)
    ctx.offset += 1
    cdef TAG_Byte tag = TAG_Byte.__new__(TAG_Byte)
    tag.value = ptr[0]
    tag.tagID = TAG_BYTE
    tag._name = u""
    return tag

    
cdef load_short(load_ctx ctx):
    ctx.require(2)
    cdef short * ptr = <short *>(ctx.buffer + ctx.offset)
    swab(ptr, 2)
    ctx.offset += 2
    cdef TAG_Short tag = TAG_Short.__new__(TAG_Short)
    tag.value = ptr[0]
    tag.tagID = TAG_SHORT
    tag._name = u""
    return tag

    
cdef load_int(load_ctx ctx):
    ctx.require(4)
    cdef int * ptr = <int *>(ctx.buffer + ctx.offset)
    swab(ptr, 4)
    ctx.offset += 4
    cdef TAG_Int tag = TAG_Int.__new__(TAG_Int)
    tag.value = (ptr[0])
    tag.tagID = TAG_INT
    tag._name = u""
    return tag
    
cdef load_long(load_ctx ctx):
    ctx.require(8)
    cdef long long * ptr = <long long *>(ctx.buffer + ctx.offset)
    swab(ptr, 8)
    ctx.offset += 8
    cdef TAG_Long tag = TAG_Long.__new__(TAG_Long)
    tag.value = ptr[0]
    tag.tagID = TAG_LONG
    tag._name = u""
    return tag

    
cdef load_float(load_ctx ctx):
    ctx.require(4)
    cdef float * ptr = <float *>(ctx.buffer + ctx.offset)
    swab(ptr, 4)
    ctx.offset += 4
    cdef TAG_Float tag = TAG_Float.__new__(TAG_Float)
    tag.value = ptr[0]
    tag.tagID = TAG_FLOAT
    tag._name = u""
    return tag

    
cdef load_double(load_ctx ctx):
    ctx.require(8)
    cdef double * ptr = <double *>(ctx.buffer + ctx.offset)
    swab(ptr, 8)
    ctx.offset += 8
    cdef TAG_Double tag = TAG_Double.__new__(TAG_Double)
    tag.value = ptr[0]
    tag.tagID = TAG_DOUBLE
    tag._name = u""
    return tag

    
cdef load_bytearray(load_ctx ctx):
    ctx.require(4)
    cdef unsigned int * ptr = <unsigned int *>(ctx.buffer + ctx.offset)
    swab(ptr, 4)
    cdef unsigned int length = ptr[0]
    ctx.offset += 4
    cdef char * arr = ctx.buffer + ctx.offset
    #print "Bytearray", length, ctx.size - ctx.offset
    ctx.require(length)
    ctx.offset += length
    return TAG_Byte_Array(fromstring(arr[:length], dtype='uint8', count=length))

cdef load_intarray(load_ctx ctx):
    ctx.require(4)
    cdef unsigned int * ptr = <unsigned int *>(ctx.buffer + ctx.offset)
    swab(ptr, 4)
    cdef unsigned int length = ptr[0]
    ctx.offset += 4
    cdef char * arr = ctx.buffer + ctx.offset
    #print "Bytearray", length, ctx.size - ctx.offset
    bytelength = length*4
    ctx.require(bytelength)
    ctx.offset += bytelength
    return TAG_Int_Array(fromstring(arr[:bytelength], dtype='>u4', count=length))


### --- load_compound ---
cdef load_compound(load_ctx ctx):
    #print "load_compound buf=%d off=%d" % (ctx.buffer[0], ctx.offset)
    cdef char tagID
    cdef _TAG_Compound root_tag = TAG_Compound()
    assert root_tag is not None
    
    while True:
        ctx.require(1)
        tagID = ctx.buffer[ctx.offset]
        ctx.offset += 1
        if tagID == TAG_END:
            #print "TAG_END at ", ctx.offset
            break
        else:
            name = load_string(ctx)
            tag = load_tag(tagID, ctx)
            #tag.name = name
            #print "tagID=%d name=%s at %d" % (tagID, tag.name, ctx.offset)
            root_tag[name] = tag
    return root_tag
         
cdef load_list(load_ctx ctx):
    ctx.require(5)
    cdef char tagID = ctx.buffer[ctx.offset]
    ctx.offset += 1
    cdef int * ptr = <int *>(ctx.buffer + ctx.offset)
    swab(ptr, 4)
    ctx.offset += 4
    length = ptr[0]
    cdef _TAG_List tag = TAG_List()
    cdef list val = tag.value
    cdef int i
    for i in range(length):
        PyList_Append(val, load_tag(tagID, ctx))
    
    return tag
        
cdef unicode load_string(load_ctx ctx):
    ctx.require(2)
    cdef unsigned short * ptr = <unsigned short *>(ctx.buffer+ctx.offset)
    swab(ptr, 2)
    ctx.offset += 2
    cdef unsigned short length = ptr[0]
    #print "String: ", ctx.offset, length
    cdef unicode u = PyUnicode_DecodeUTF8(ctx.buffer + ctx.offset, length, "strict")
    ctx.offset += length
    return u

cdef load_tag(char tagID, load_ctx ctx):
    
        
    if tagID == TAG_BYTE:
        return load_byte(ctx)

    if tagID == TAG_SHORT:
        return load_short(ctx)

    if tagID == TAG_INT:
        return load_int(ctx)

    if tagID == TAG_LONG:
        return load_long(ctx)

    if tagID == TAG_FLOAT:
        return load_float(ctx)
    
    if tagID == TAG_DOUBLE:
        return load_double(ctx)

    if tagID == TAG_BYTE_ARRAY:
        return load_bytearray(ctx)
    
    if tagID == TAG_STRING:
        u = load_string(ctx)
        return TAG_String(u)
        
    if tagID == TAG_LIST:
        return load_list(ctx)
    if tagID == TAG_COMPOUND:
        return load_compound(ctx)
        
        
    if tagID == TAG_INT_ARRAY:
        return load_intarray(ctx)

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])            
def dump(src, length=8):
    N=0; result=''
    while src:
        s,src = src[:length],src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
        N+=length
    return result
    
cdef save_root_tag(tag, filename = "", buf = None):
    sio = StringIO()
    save_tag(tag, sio)
    data = sio.getvalue()
    if buf is None:
        f = file(filename, "wb")
        gzio = StringIO()
        gz = gzip.GzipFile(fileobj=gzio, mode='wb', compresslevel=2)
        gz.write(data)
        gz.close()
        f.write(gzio.getvalue())
    else:
        buf.write(data)
    
cdef save_tag(TAG_Value tag, object buf):
    save_tag_id(tag.tagID, buf)
    save_tag_name(tag, buf)
    save_tag_value(tag, buf)
    
cdef save_tag_id(char tagID, object buf):
    cwrite(buf, &tagID, 1)
    
cdef save_tag_name(TAG_Value tag, object buf):
    name = tag.name.encode('utf-8')
    save_string(name, buf)

cdef save_string(bytes value, object buf):
    cdef unsigned short length = len(value)
    cdef char * s = value
    swab(&length, 2)
    cwrite(buf, <char *>&length, 2)
    cwrite(buf, s, len(value))
    
cdef save_byte_array(object value, object buf):
    value = value.tostring()
    cdef char * s = value
    cdef unsigned int length = len(value)
    swab(&length, 4)
    cwrite(buf, <char *>&length, 4)
    cwrite(buf, s, len(value))

cdef save_int_array(object value, object buf):
    value = value.tostring()
    cdef char * s = value
    cdef unsigned int length = len(value) / 4
    swab(&length, 4)
    cwrite(buf, <char *>&length, 4)
    cwrite(buf, s, len(value))

cdef save_byte(char value, object buf):
    cwrite(buf, <char *>&value, 1)

cdef save_short(short value, object buf):
    swab(&value, 2)
    cwrite(buf, <char *>&value, 2)

cdef save_int(int value, object buf):
    swab(&value, 4)
    cwrite(buf, <char *>&value, 4)

cdef save_long(long long value, object buf):
#    print "Long long value: ", value, sizeof(value)
    swab(&value, 8)
    cdef char * p = <char *>&value
    cwrite(buf, p, 8)
    #cwrite(buf, p+4, 4)
    #cwrite(buf, "\0\0\0\0\0\0\0\0", 8)

cdef save_float(float value, object buf):
    swab(&value, 4)
    cwrite(buf, <char *>&value, 4)

cdef save_double(double value, object buf):
    swab(&value, 8)
    cwrite(buf, <char *>&value, 8)

cdef save_tag_value(TAG_Value tag, object buf):
    cdef char tagID = tag.tagID
    if tagID == TAG_BYTE:
        (<TAG_Byte>tag).save_value(buf)

    if tagID == TAG_SHORT:
        (<TAG_Short>tag).save_value(buf)

    if tagID == TAG_INT:
        (<TAG_Int>tag).save_value(buf)

    if tagID == TAG_LONG:
        (<TAG_Long>tag).save_value(buf)

    if tagID == TAG_FLOAT:
        (<TAG_Float>tag).save_value(buf)
    
    if tagID == TAG_DOUBLE:
        (<TAG_Double>tag).save_value(buf)

    if tagID == TAG_BYTE_ARRAY:
        (<TAG_Byte_Array>tag).save_value(buf)
    
    if tagID == TAG_STRING:
        (<TAG_String>tag).save_value(buf)
        
    if tagID == TAG_LIST:
        (<_TAG_List>tag).save_value(buf)
    if tagID == TAG_COMPOUND:
        (<_TAG_Compound>tag).save_value(buf)
        
        
    if tagID == TAG_INT_ARRAY:
        (<TAG_Int_Array>tag).save_value(buf)
    
