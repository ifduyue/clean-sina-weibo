#!/usr/bin/env python
#-*- coding: utf8 -*-
from struct import *
import re

def is_ipv4(str):
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(str) is not None
    
def is_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros 
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None
    
def is_ip(str):
    return is_ipv4(str) or is_ipv6(str)
    
def extract_text(str):
    if not isinstance(str, unicode):
        try:
            str = mb_code(str).decode('utf8')
        except:
            return str
    a = u'\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19\uff10\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u96f6\u2488\u2489\u248a\u248b\u248c\u248d\u248e\u248f\u2490\u2491\u2474\u2475\u2476\u2477\u2478\u2479\u247a\u247b\u247c\u247d\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469\u3220\u3221\u3222\u3223\u3224\u3225\u3226\u3227\u3228\u3229\uff41\uff42\uff43\uff44\uff45\uff46\uff47\uff48\uff49\uff4a\uff4b\uff4c\uff4d\uff4e\uff4f\uff50\uff51\uff52\uff53\uff54\uff55\uff56\uff57\uff58\uff59\uff5a\uff21\uff22\uff23\uff24\uff25\uff26\uff27\uff28\uff29\uff2a\uff2b\uff2c\uff2d\uff2e\uff2f\uff30\uff31\uff32\uff33\uff34\uff35\uff36\uff37\uff38\uff39\uff3a\uff0d\uff1d\uff3b\uff3d\u3001\uff1b\uff40\uff07\u2018\u2019\uff0c\u3002\uff0f\uff5e\uff01\xb7\uff03\uffe5\uff05\ufe3f\uff06\uff0a\u203b\uff08\uff09\u2014\uff0b\uff5b\uff5d\uff5c\uff1a\u300a\u300b\uff1f\u2026\uff3c\uff0e\uff20\uff04\uff3f\u201c\uff02\u201d\uff1c\uff1e\u3000\u3008\u3009\u3010\u3011'
    b = u'1234567890123456789012345678901234567890123456789012345678901234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-=[],;`\'`\',./~!.#$%^&**()-+{}|:<>?.\\.@$_"""<> <>[]'
    table = dict(zip([ord(i) for i in a], b))
    #table = {19968: u'1', 12289: u',', 12290: u'.', 19971: u'7', 12296: u'<', 19977: u'3', 12298: u'<', 12299: u'>', 12304: u'[', 12305: u']', 8212: u'-', 8216: u'`', 8217: u"'", 8220: u'"', 8221: u'"', 12832: u'1', 12833: u'2', 12834: u'3', 12835: u'4', 12836: u'5', 12837: u'6', 12838: u'7', 12839: u'8', 12840: u'9', 12841: u'0', 12297: u'>', 8251: u'*', 65087: u'^', 38470: u'6', 65293: u'-', 20061: u'9', 9312: u'1', 9313: u'2', 9314: u'3', 9315: u'4', 9316: u'5', 9317: u'6', 9318: u'7', 9319: u'8', 9320: u'9', 9321: u'0', 9332: u'1', 9333: u'2', 9334: u'3', 9335: u'4', 9336: u'5', 9337: u'6', 9338: u'7', 9339: u'8', 9340: u'9', 9341: u'0', 32902: u'4', 9352: u'1', 9353: u'2', 9354: u'3', 9355: u'4', 20108: u'2', 9357: u'6', 9358: u'7', 9359: u'8', 9360: u'9', 9361: u'0', 20116: u'5', 183: u'.', 22235: u'4', 8230: u'.', 38646: u'0', 22777: u'1', 65281: u'!', 65282: u'"', 65283: u'#', 65284: u'$', 65285: u'%', 65286: u'&', 65287: u"'", 65288: u'(', 65289: u')', 65290: u'*', 65291: u'+', 65292: u',', 20237: u'5', 65294: u'.', 65295: u'/', 65296: u'0', 65297: u'1', 65298: u'2', 65299: u'3', 65300: u'4', 65301: u'5', 65302: u'6', 65303: u'7', 65304: u'8', 65305: u'9', 65306: u':', 65307: u';', 65308: u'<', 65309: u'=', 65310: u'>', 65311: u'?', 65312: u'@', 65313: u'A', 65314: u'B', 65315: u'C', 65316: u'D', 65317: u'E', 65318: u'F', 65319: u'G', 65320: u'H', 65321: u'I', 65322: u'J', 65323: u'K', 65324: u'L', 65325: u'M', 65326: u'N', 65327: u'O', 36144: u'2', 65329: u'Q', 65330: u'R', 65331: u'S', 65332: u'T', 65333: u'U', 65334: u'V', 65335: u'W', 65336: u'X', 65337: u'Y', 65338: u'Z', 65339: u'[', 65340: u'\\', 65341: u']', 65343: u'_', 65344: u'`', 65345: u'a', 65346: u'b', 65347: u'c', 65348: u'd', 65349: u'e', 65350: u'f', 65351: u'g', 65352: u'h', 65353: u'i', 65354: u'j', 65355: u'k', 25420: u'8', 65357: u'm', 65358: u'n', 65359: u'o', 65360: u'p', 65361: u'q', 65362: u'r', 65363: u's', 65364: u't', 65365: u'u', 65366: u'v', 65367: u'w', 65368: u'x', 65369: u'y', 65370: u'z', 65371: u'{', 65372: u'|', 65373: u'}', 65374: u'~', 20843: u'8', 20845: u'6', 12288: u' ', 9356: u'5', 29590: u'9', 65328: u'P', 21441: u'3', 65356: u'l', 26578: u'7', 65509: u'$'}
    table_no_punct = dict((ord(i), u'') for i in u'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\x0b\x0c\r ')
    return str.translate(table).translate(table_no_punct)
    

def mb_code(str, coding="utf-8"):
    if isinstance(str, unicode):
        return str.encode(coding)
    for c in ('utf-8', 'gb18030', 'gbk', 'gb2312'):
        try:
            return str.decode(c).encode(coding)
        except:
            pass
    return str
 
def ip2string( ip ):
    a = (ip & 0xff000000) >> 24
    b = (ip & 0x00ff0000) >> 16
    c = (ip & 0x0000ff00) >> 8
    d = ip & 0x000000ff
    return "%d.%d.%d.%d" % (a,b,c,d)
 
def string2ip( str ):
    ss = str.split('.')
    ip = 0L
    for s in ss: ip = (ip << 8) + int(s)
    return ip
 
class IpLocater :
    def __init__( self, ipdb_file ):
        self.ipdb = open( ipdb_file, "rb" )
        # get index address 
        str = self.ipdb.read( 8 )
        (self.first_index,self.last_index) = unpack('II',str)
        self.index_count = (self.last_index - self.first_index) / 7 + 1
 
    def getString(self,offset = 0):
        if offset :
            self.ipdb.seek( offset )
        str = ""
        while True:
            ch = self.ipdb.read(1)
            (byte, ) = unpack('B', ch)
            if byte == 0:
                break
            str += ch
        return str
 
    def getLong3(self,offset = 0):
        if offset :
            self.ipdb.seek( offset )
        str = self.ipdb.read(3)
        (a,b) = unpack('HB',str)
        return (b << 16) + a
 
    def getAreaAddr(self,offset=0):
        if offset :
            self.ipdb.seek( offset )
        str = self.ipdb.read( 1 )
        (byte,) = unpack('B',str)
        if byte == 0x01 or byte == 0x02:
            p = self.getLong3()
            if p:
                return self.getString( p )
            else:
                return ""
        else:
            return self.getString( offset )
 
    def getAddr(self,offset ,ip = 0):
        self.ipdb.seek( offset + 4)
 
        countryAddr = ""
        areaAddr = ""
        str = self.ipdb.read( 1 )
        (byte,) = unpack('B',str)
        if byte == 0x01:
            countryOffset = self.getLong3()
            self.ipdb.seek(countryOffset )
            str = self.ipdb.read( 1 )
            (b,) = unpack('B',str)
            if b == 0x02:
                countryAddr = self.getString( self.getLong3() )
                self.ipdb.seek( countryOffset + 4 )
            else:
                countryAddr = self.getString( countryOffset )
            areaAddr = self.getAreaAddr()
        elif byte == 0x02:
            countryAddr = self.getString( self.getLong3() )
            areaAddr = self.getAreaAddr( offset + 8 )
        else:
            countryAddr = self.getString( offset + 4 )
            areaAddr = self.getAreaAddr( )
        
        return mb_code(countryAddr), mb_code(areaAddr)
 
    def output(self, first ,last ):
        if last > self.index_count :
            last = self.index_count
        for index in range(first,last):
            offset = self.first_index + index * 7
            self.ipdb.seek( offset )
            buf = self.ipdb.read( 7 )
            (ip,of1,of2) = unpack("IHB",buf)
            print "%s - %s" % (ip2string(ip), self.getAddr( of1 + (of2 << 16) ) )
 
    def find(self,ip,left,right):
        if right-left == 1:
            return left
        else:
            middle = ( left + right ) / 2
            offset = self.first_index + middle * 7
            self.ipdb.seek( offset )
            buf = self.ipdb.read( 4 )
            (new_ip,) = unpack("I",buf)
            if ip <= new_ip :
                return self.find( ip, left, middle )
            else:
                return self.find( ip, middle, right )
 
    def getIpAddr(self,ip):
        index = self.find( ip,0,self.index_count - 1 )
        ioffset = self.first_index + index * 7
        aoffset = self.getLong3( ioffset + 4)
        address = self.getAddr( aoffset )
        address = [i.replace('CZ88.NET', '') for i in address]
        return address                
 
if __name__ == "__main__" :
    ip_locater = IpLocater( "QQWry.Dat" )
    #ip_locater.output( 0, ip_locater.index_count )
    ip = '59.64.234.174'
    ip = '0.0.0.1'
    address = ip_locater.getIpAddr( string2ip( ip ) )
    print "the ip %s come from %s" % (ip,address)