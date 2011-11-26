
# vim:set sw=2 sts=2 ts=2:

"""
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
from cStringIO import StringIO;
import os;
from contextlib import closing
from numpy import array, zeros, uint8, fromstring
TAGfmt = ">b"

class NBTFormatError(RuntimeError): pass

class TAG_Value(object):
    """Simple values. Subclasses override fmt to change the type and size. 
    Subclasses may set dataType instead of overriding setValue for automatic data type coercion"""

    fmt = ">b";
    tag = -1; #error!

    _value = None
    def getValue(self):
            return self._value
    def setValue(self, newVal):
            self._value = self.dataType(newVal)
    value = property(getValue, setValue, None, "Change the TAG's value.    Data types are checked and coerced if needed.")

    _name = None
    def getName(self):
            return self._name
    def setName(self, newVal):
            self._name = str(newVal)
    def delName(self):
            self._name = ""
    name = property(getName, setName, delName, "Change the TAG's name.    Coerced to a string.")
    
    @classmethod
    def load_from(cls, data, data_cursor):
        data = data[data_cursor:]
        (value,) = struct.unpack_from(cls.fmt, data);
        self = cls(value=value)
        return self, data_cursor + struct.calcsize(self.fmt)
        
    def __init__(self, value=0, name=None):
        self.name = name
        self.value = value
        
            

    def __repr__(self):
        return "%s( \"%s\" ): %s" % (str(self.__class__), self.name, repr(self.value))

    def __str__(self):
        return self.pretty_string()

    def pretty_string(self, indent=0):
        if self.name:
            return  " " * indent + "%s( \"%s\" ): %s" % (str(self.__class__.__name__), self.name, self.value)
        else:
            return  " " * indent + "%s: %s" % (str(self.__class__.__name__), self.value)


    def write_tag(self, buf):
        buf.write(struct.pack(TAGfmt, self.tag))
    def write_name(self, buf):
        if(self.name != None):
            TAG_String(self.name).write_value(buf)
    def write_value(self, buf):
        buf.write(struct.pack(self.fmt, self.value))

    def save(self, filename="", buf=None):
        if(filename):
            self.saveGzipped(filename);
            return;
        "Save the tagged element to a file."
        if self.name == None: self.name = "" #root tag must have name
        self.write_tag(buf)
        self.write_name(buf)
        self.write_value(buf)

    def saveGzipped(self, filename, compresslevel=1):
        sio = StringIO();
        #atomic write
        try: os.rename(filename, filename + ".old");
        except Exception, e:
            #print "Atomic Save: No existing file to rename"
            pass

        with closing(gzip.GzipFile(fileobj=sio, mode="wb", compresslevel=compresslevel)) as outputGz:
                self.save(buf=outputGz);
                outputGz.flush();

        #print len(sio.getvalue());
        try:
                with open(filename, 'wb') as f:
                        f.write(sio.getvalue());
        except:
            try:
                os.rename(filename + ".old", filename,);
            except Exception, e:
                print e;
                return

        try: os.remove(filename + ".old");
        except Exception, e:
            #print "Atomic Save: No old file to remove"
            pass;

class TAG_Byte(TAG_Value):
    tag = 1;
    fmt = ">b";
    dataType = int

class TAG_Short(TAG_Value):
    tag = 2;
    fmt = ">h";
    dataType = int

class TAG_Int(TAG_Value):
    tag = 3;
    fmt = ">i";
    dataType = int

class TAG_Long(TAG_Value):
    tag = 4;
    fmt = ">q";
    dataType = long

class TAG_Float(TAG_Value):
    tag = 5;
    fmt = ">f";
    dataType = float


class TAG_Double(TAG_Value):
    tag = 6;
    fmt = ">d";
    dataType = float


class TAG_Byte_Array(TAG_Value):
    """Like a string, but for binary data.    four length bytes instead of
    two.    value is a numpy array, and you can change its elements"""

    tag = 7;
    fmt = ">i%ds"

    def dataType(self, value):
        return array(value, uint8)

    def __repr__(self):
        return "<%s: length %d> ( %s )" % (self.__class__, len(self.value), self.name)


    def pretty_string(self, indent=0):
        if self.name:
            return  " " * indent + "%s( \"%s\" ): shape=%s dtype=%s %s" % (
                str(self.__class__.__name__),
                self.name,
                str(self.value.shape),
                str(self.value.dtype),
                self.value)
        else:
            return  " " * indent + "%s: %s %s" % (str(self.__class__.__name__), str(self.value.shape), self.value)
    
    @classmethod
    def load_from(cls, data, data_cursor):
        data = data[data_cursor:]
        (string_len,) = struct.unpack_from(">I", data);
        value = fromstring(data[4:string_len + 4], 'uint8');
        self = cls(value)
        return self, data_cursor + string_len + 4
        
    def __init__(self, value=zeros(0, uint8), name=None):
        if name:
            self.name = name
        self.value = value;
        

    def write_value(self, buf):
        #print self.value
        valuestr = self.value.tostring()
        buf.write(struct.pack(self.fmt % (len(valuestr),), len(valuestr), valuestr))

class TAG_Int_Array(TAG_Byte_Array):
    """An array of ints"""
    tag = 11;
    def dataType(self, value):
        return array(value, '>u4')
    
    @classmethod
    def load_from(cls, data, data_cursor):
        data = data[data_cursor:]
        (string_len,) = struct.unpack_from(">I", data);
        value = fromstring(data[4:string_len * 4 + 4], '>u4')
        self = cls(value)
        return self, data_cursor + len(self.value) * 4 + 4;
        
    def __init__(self, value=zeros(0, ">u4"), name=None):
        self.name = name
        self.value = value;


    def write_value(self, buf):
        #print self.value
        valuestr = self.value.tostring()
        buf.write(struct.pack(self.fmt % (len(valuestr),), len(valuestr) / 4, valuestr))

class TAG_Short_Array(TAG_Int_Array):
    """An array of ints"""
    tag = 12;
    def dataType(self, value):
        return array(value, '>u2')

    @classmethod
    def load_from(cls, data, data_cursor):
        data = data[data_cursor:]
        (string_len,) = struct.unpack_from(">I", data);
        value = fromstring(data[4:string_len * 2 + 4], '>u2')
        self = cls(value)
        return self, data_cursor + len(self.value) * 2 + 4;
        
    def __init__(self, value=zeros(0, ">u2"), name=None):
        self.name = name
        self.value = value;


    def write_value(self, buf):
        #print self.value
        valuestr = self.value.tostring()
        buf.write(struct.pack(self.fmt % (len(valuestr),), len(valuestr) / 2, valuestr))

class TAG_String(TAG_Value):
    """String in UTF-8
    The value parameter must be a 'unicode' or a UTF-8 encoded 'str'
    """

    tag = 8;
    fmt = ">h%ds"
    dataType = lambda self, s: isinstance(s, unicode) and s.encode('utf-8') or s

    @classmethod
    def load_from(cls, data, data_cursor):
        data = data[data_cursor:]
        (string_len,) = struct.unpack_from(">H", data);
        value = data[2:string_len + 2].tostring();
        self = cls(value)
        return self, data_cursor + string_len + 2;

    def __init__(self, value="", name=None):
        if name:
            self.name = name
        self.value = value

    def write_value(self, buf):
        u8value = self._value
        buf.write(struct.pack(self.fmt % (len(u8value),), len(u8value), u8value))

    @property
    def unicodeValue(self):
        return self.value.decode('utf-8')
    
            

class TAG_Compound(TAG_Value, collections.MutableMapping):
    """A heterogenous list of named tags. Names must be unique within
    the TAG_Compound. Add tags to the compound using the subscript
    operator [].    This will automatically name the tags."""

    tag = 10;

    def dataType(self, val):
            for i in val:
                    assert isinstance(i, TAG_Value)
                    assert i.name
            return list(val)

    def __repr__(self):
        return "%s( %s ): %s" % (str(self.__class__.__name__), self.name, self.value)

    def pretty_string(self, indent=0):
        if self.name:
            pretty = " " * indent + "%s( \"%s\" ): %d items\n" % (str(self.__class__.__name__), self.name, len(self.value))
        else:
            pretty = " " * indent + "%s(): %d items\n" % (str(self.__class__.__name__), len(self.value))
        indent += 4
        for tag in self.value:
            pretty += tag.pretty_string(indent) + "\n"
        return pretty

    @classmethod
    def load_from(cls, data, data_cursor):
        self = cls()
        while data_cursor < len(data):
            tag_type = data[data_cursor];
            data_cursor += 1
            if(tag_type == 0):
                break

            tag, data_cursor = load_named(data, data_cursor, tag_type)

            self._value.append(tag);
        
        return self, data_cursor
        
    def __init__(self, value=[], name=""):

        self.name = name;
        if value.__class__ == ''.__class__:
            self.name = value;
            value = [];
        self.value = value;
        
            

    def write_value(self, buf):
        for i in self.value:
            i.save(buf=buf)
        buf.write("\x00")

    "collection functions"
    def __getitem__(self, k):
        #hits=filter(lambda x:x.name==k, self.value);
        #if(len(hits)): return hits[0];
        for key in self.value:
                if key.name == k: return key
        raise KeyError("Key {0} not found in tag {1}".format(k, self));

    def __iter__(self):             return itertools.imap(lambda x:x.name, self.value);
    def __contains__(self, k):return k in map(lambda x:x.name, self.value);
    def __len__(self):                return self.value.__len__()


    def __setitem__(self, k, v):
        """Automatically wraps lists and tuples in a TAG_List, and wraps strings
        and unicodes in a TAG_String."""
        if isinstance(v, (list, tuple)):
            v = TAG_List(v)
        elif isinstance(v, basestring):
            v = TAG_String(v)

        if not (v.__class__ in tag_classes.values()): raise TypeError("Invalid type %s for TAG_Compound" % (v.__class__))
        """remove any items already named "k".    """
        olditems = filter(lambda x:x.name == k, self.value)
        for i in olditems: self.value.remove(i)
        self.value.append(v);
        v.name = k;

    def __delitem__(self, k): self.value.__delitem__(self.value.index(self[k]));

    def add(self, v):
        self[v.name] = v;

class TAG_List(TAG_Value, collections.MutableSequence):

    """A homogenous list of unnamed data of a single TAG_* type. 
    Once created, the type can only be changed by emptying the list 
    and adding an element of the new type. If created with no arguments,
    returns a list of TAG_Compound
    
    Empty lists in the wild have been seen with type TAG_Byte"""

    tag = 9;

    def dataType(self, val):
        if val:
            listType = val[0].__class__
            # FIXME: This is kinda weird; None as the empty tag name?
            assert all(isinstance(x, listType) and x.name in ("", "None") for x in val)
        return list(val)

    def __repr__(self):
        return "%s( %s ): %s" % (self.__class__.__name__, self.name, self.value)


    def pretty_string(self, indent=0):
        if self.name:
            pretty = " " * indent + "%s( \"%s\" ):\n" % (str(self.__class__.__name__), self.name)
        else:
            pretty = " " * indent + "%s():\n" % (str(self.__class__.__name__),)

        indent += 4
        for tag in self.value:
            pretty += tag.pretty_string(indent) + "\n"
        return pretty
    
    @classmethod
    def load_from(cls, data, data_cursor):
        self = cls()
        self.list_type = data[data_cursor];
        
        data_cursor += 1;

        list_length, data_cursor = TAG_Int.load_from(data, data_cursor)
        list_length = list_length.value


        for i in range(list_length):

            tag, data_cursor = tag_classes[self.list_type].load_from(data, data_cursor)
            self.append(tag);
        
        return self, data_cursor
        
    def __init__(self, value=[], name=None, list_type=TAG_Compound):
        #can be created from a list of tags in value, with an optional
        #name, or created from raw tag data, or created with list_type
        #taken from a TAG class or instance

        self.name = name
        self.list_type = list_type.tag

        if(len(value)):
            self.list_type = value[0].tag;
            value = filter(lambda x:x.__class__ == value[0].__class__, value)

        self.value = value
            

    """ collection methods """
    def __iter__(self):             return iter(self.value)
    def __contains__(self, k):return k in self.value;
    def __getitem__(self, i): return self.value[i];
    def __len__(self):                return len(self.value)

    def __setitem__(self, i, v):
        if v.__class__ != tag_classes[self.list_type]:
            raise TypeError("Invalid type %s for TAG_List(%s)" % (v.__class__, tag_classes[self.list_type]))
        v.name = ""
        self.value[i] = v;

    def __delitem__(self, i):
        del self.value[i]

    def insert(self, i, v):
            if not v.tag in tag_classes: raise TypeError("Not a tag type: %s" % (v,))
            if len(self) == 0:
                    self.list_type = v.tag
            else:
                    if v.__class__ != tag_classes[self.list_type]: raise TypeError("Invalid type %s for TAG_List(%s)" % (v.__class__, tag_classes[self.list_type]))

            v.name = ""
            self.value.insert(i, v);

    def write_value(self, buf):
        buf.write(struct.pack(TAGfmt, self.list_type))
        TAG_Int(len(self)).write_value(buf)
        for i in self.value:
            i.write_value(buf)


tag_classes = {
    1 : TAG_Byte,
    2 : TAG_Short,
    3 : TAG_Int,
    4 : TAG_Long,
    5 : TAG_Float,
    6 : TAG_Double,
    7 : TAG_Byte_Array,
    8 : TAG_String,
    9 : TAG_List,
    10: TAG_Compound,
    11: TAG_Int_Array,
    12: TAG_Short_Array,
    };

import zlib
def gunzip(data):
    #strip off the header and use negative WBITS to tell zlib there's no header
    return zlib.decompress(data[10:], -zlib.MAX_WBITS)

def loadFile(filename):
    with file(filename, "rb") as f:
        inputdata = f.read()
    data = inputdata
    try:
        data = gunzip(inputdata)
    except IOError:
        print "File %s not zipped" % filename

    return load(buf=fromstring(data, 'uint8'));

def load_named(data, data_cursor, tag_type):
    tag_name, data_cursor = TAG_String.load_from(data, data_cursor)
    tag_name = tag_name.value

    tag, data_cursor = tag_classes[tag_type].load_from(data, data_cursor)
    tag.name = tag_name
    
    return tag, data_cursor

def load(filename="", buf=None):
    """Unserialize data from an entire NBT file and return the 
    root TAG_Compound object. Argument can be a string containing a 
    filename or an array of integers containing TAG_Compound data. """

    if filename and isinstance(filename, (str, unicode)):
        return loadFile(filename)
    if isinstance(buf, str): buf = fromstring(buf, uint8)
    data = buf;
    #if buf != None: data = buf
    if not len(buf):
        raise NBTFormatError, "Asked to load root tag of zero length"

    data_cursor = 0;
    tag_type = data[data_cursor];
    if tag_type != 10:
        raise NBTFormatError, 'Not an NBT file with a root TAG_Compound (found {0})'.format(tag_type);
    data_cursor += 1;

    tag, data_cursor = load_named(data, data_cursor, tag_type)

    return tag;



__all__ = [a.__name__ for a in tag_classes.itervalues()] + ["load", "loadFile", "gunzip"]


