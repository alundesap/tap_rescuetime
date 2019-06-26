from mitmproxy import ctx
from requests_toolbelt.multipart import decoder
import gzip
import zlib
import re
import io
import base64


def dump(obj):
    for attr in dir(obj):
        if hasattr( obj, attr ):
            #print( "obj.%s = %s" % (attr, getattr(obj, attr)))
            ctx.log.info( "obj.%s = %s" % (attr, getattr(obj, attr)))

class Counter:
    def __init__(self):
        self.num = 0

    def request(self, flow):
        self.num = self.num + 1
        ctx.log.info("We've seen %d flowz" % self.num)
        ctx.log.info("url: %s" % flow.request.url)
        if "Host" in flow.request.headers:
            ctx.log.info("host: %s" % flow.request.headers["Host"])
            if flow.request.headers["Host"] == "api.rescuetime.com":
                ctx.log.info("RescueTime API!")
                if "Content-Type" in flow.request.headers:
                    ctx.log.info("Content-Type Exists!")
                    cont_type = flow.request.headers["Content-Type"]
                    cont_len = flow.request.headers["Content-Length"]
                    ctx.log.info("cont_type: %s" % cont_len + "=" + cont_type)
                    mp_type, mp_bound = cont_type.split(';')
                    if flow.request.url == "https://api.rescuetime.com/config":
                        ctx.log.info("rt_post_type: %s" % "config")
                    elif flow.request.url == "https://api.rescuetime.com/messages":
                        ctx.log.info("rt_post_type: %s" % "messages")
                    elif flow.request.url == "https://api.rescuetime.com/collect":
                        ctx.log.info("rt_post_type: %s" % "collect")
# https://mitmproxy.readthedocs.io/en/v2.0.2/scripting/api.html#mitmproxy.http.HTTPRequest
# https://mitmproxy.readthedocs.io/en/v2.0.2/
                        if mp_type == "multipart/form-data":
                            #mpfd.body = flow.request.content
                            #mpfd.type = mp_type
                            #mpfd.boundary = mp_bound
                            #mp_data = decoder.MultipartDecoder(flow.request)
                            #dump(flow.request)
                            for key in flow.request.multipart_form:
                                #ctx.log.info("key: %s" % key.decode("utf-8") + " = " + flow.request.multipart_form[key])
                                dkey = key.decode("utf-8")
                                if dkey == "account_key":
                                    acct = flow.request.multipart_form[key].decode("utf-8")
                                    ctx.log.info("account: %s" % acct)
                                elif dkey == "file":
                                    ctx.log.info("key: %s" % dkey)
                                    #gzdat = flow.request.multipart_form[key]   # Somehow strips out "0A"
                                    boundary = cont_type.split(";")[1].strip().replace("boundary=","")
                                    ctx.log.info("boundary: %s" % boundary)
                                    #f = open("boundary.bin", "wt")
                                    #f.write(boundary)
                                    #f.close()
                                    content = flow.request.content
                                    parts = content.split(bytes(boundary,'utf-8'))
                                    last = parts[len(parts)-2]
                                    
                                    gzdat = last.split(bytes("\r\n",'utf-8'))[4]

                                    ctx.log.info("data: %s" % "rt.gz")
                                    #f = open("rt.gz", "wb")
                                    #f.write(gzdat)
                                    #f.close()

                                    #undat = gzip.decompress(gzdat)

                                    #undat = zlib.decompress(gzdat)
                                    #undat = zlib.decompress(gzdat, 16+zlib.MAX_WBITS)
                                    #Decompress = zlib.decompressobj(0)
                                    #undat = Decompress.decompress(gzdat,0)
                                    #while not Decompress.eof:
                                    #    undat += Decompress.decompress(gzdat,0)
                                    undat = gzip.GzipFile(fileobj=io.BytesIO(gzdat), mode='rb').read()
                                    #f = open("rt.csv", "wb")
                                    #f.write(undat)
                                    #f.close()
                                    undat8 = undat.decode("utf-8")
                                    lines = undat8.splitlines()
                                    for bcline in lines:
                                        # Dump each line
                                        #line = bcline.decode("utf-8")
                                        line = bcline
                                        ctx.log.info("line: %s" % line)
                                        cols = line.split(',')
                                        numcols = len(cols)
                                        #ctx.log.info("numcols: %d" % numcols)
                                        #for col in cols:
                                        #    ctx.log.info("app: %s" % cols[0])
                                        app  = cols[0]
                                        uk01 = cols[1]
                                        uk02 = cols[2]
                                        doc  = cols[3]
                                        uk04 = cols[4]
                                        stime = cols[5]
                                        etime = cols[6]
                                        uk07 = cols[7]
                                        uk08 = cols[8]
                                        uk09 = cols[9]
                                        uk10 = cols[10]
                                        uk11 = cols[11]
                                        ctx.log.info("acct: %s" % acct)
                                        ctx.log.info("app: %s" % app)
                                        ctx.log.info("doc: %s" % doc)
                                        ctx.log.info("time: %s" % stime + " to " + etime)
                                else:
                                    dval = flow.request.multipart_form[key].decode("utf-8")
                                    ctx.log.info("key: %s" % dkey + " = " + dval)
                        else:
                            ctx.log.info("expected content type of multipart/form-data.")
                    else: 
                        ctx.log.info("rt_post_type: %s" % "unknown")
                else:
                    ctx.log.info("No Content-Type Exists!")
            else:
                ctx.log.info("Not RescueTime API!")
        else:
            ctx.log.info("No Host Header.")


    def response(self, flow):
        self.num = self.num + 1
        flow.response.headers["count"] = str(self.num)
        if flow.request.url == "https://api.rescuetime.com/config":
            ctx.log.info("rt_post_type: %s" % "config")
            content = flow.response.content.decode("utf-8")
            #ctx.log.info("content: %s" % content)
            tweeked = content
            tweeked = re.sub(r'.*push_interval: (.*)\n', r'  push_interval: 120\n', tweeked)
            tweeked = re.sub(r'.*pull_interval: (.*)\n', r'  pull_interval: 30\n', tweeked)
            tweeked = re.sub(r'.*premium_enabled: (.*)\n', r'  premium_enabled: true\n', tweeked)
            tweeked = re.sub(r'.*timepie_enabled: (.*)\n', r'  timepie_enabled: true\n', tweeked)
            ctx.log.info("tweeked: %s" % tweeked)
            flow.response.text = tweeked
        else: 
            ctx.log.info("rt_post_type: %s" % "unknown")


addons = [
    Counter()
]
