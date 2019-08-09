from mitmproxy import ctx
from requests_toolbelt.multipart import decoder
import gzip
import zlib
import re
import io
import base64
from hdbcli import dbapi
import csv
import os


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

                                    if "HDI_HOST" in os.environ:
                                        hdi_host = os.environ['HDI_HOST']
                                        ctx.log.info("HDI_HOST: %s" % hdi_host)

                                        if "HDI_PORT" in os.environ:
                                            hdi_port = os.environ['HDI_PORT']

                                        if "HDI_SCHEMA" in os.environ:
                                            hdi_schema = os.environ['HDI_SCHEMA']

                                        if "HDI_USER" in os.environ:
                                            hdi_user = os.environ['HDI_USER']

                                        if "HDI_PASS" in os.environ:
                                            hdi_pass = os.environ['HDI_PASS']

                                        if "HDI_CERT" in os.environ:
                                            hdi_cert = os.environ['HDI_CERT']

                                        ctx.log.info("HDI_PORT: %s" % hdi_port)
                                        ctx.log.info("HDI_SCHEMA: %s" % hdi_schema)
                                        ctx.log.info("HDI_USER: %s" % hdi_user)
                                        ctx.log.info("HDI_PASS: %s" % hdi_pass)
                                        if "HDI_CERT" in os.environ:
                                            ctx.log.info("HDI_CERT: %s" % hdi_cert)

                                        # https://pypi.org/project/hdbcli/
                                        try:
                                            if "HDI_CERT" in os.environ:
                                                conn = dbapi.connect(
                                                    address=hdi_host,
                                                    port=int(hdi_port),
                                                    user=hdi_user,
                                                    password=hdi_pass,
                                                    currentSchema=hdi_schema,
                                                    encrypt="true",
                                                    sslValidateCertificate="true",
                                                    sslCryptoProvider="openssl",
                                                    sslTrustStore=hdi_cert
                                                )

                                            else:
                                                conn = dbapi.connect(address=hdi_host,port=int(hdi_port),schema=hdi_schema,user=hdi_user,password=hdi_pass)
                                            undat8 = undat.decode("utf-8")
                                            lines = undat8.splitlines()
                                            #data = io.StringIO(undat8)
                                            reader = csv.reader(lines, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)

                                            cursor = conn.cursor()

                                            cursor.execute("SELECT NOW() FROM DUMMY")
                                            for row in cursor:
                                                ctx.log.info("server time1: %s" % row)


                                            sql = 'insert into "' + hdi_schema + '"."RESCUETIME_SLICES" (ID, MODIFIEDAT, CREATEDAT, CREATEDBY, MODIFIEDBY, VALIDFROM, VALIDTO, ACCOUNT, APPLICATION, DOCUMENT) values(NEWUID(),NOW(),NOW(),'"'"'mitm'"'"','"'"'mitm'"'"',?,?,?,?,?)'
                                            #ctx.log.info("sql: %s" % sql)

                                            for l in reader:
                                                app   = l[0]
                                                doc   = l[3]
                                                stime = l[5]
                                                etime = l[6]
                                                ctx.log.info("===============")
                                                ctx.log.info("acct: %s" % acct)
                                                ctx.log.info("app: %s" % app)
                                                ctx.log.info("doc: %s" % doc)
                                                ctx.log.info("time: %s" % stime + " to " + etime)

                                                # https://help.sap.com/viewer/0eec0d68141541d1b07893a39944924e/2.0.04/en-US/f3b8fabf34324302b123297cdbe710f0.html

#insert into "RESCUETIME_SLICES" values('','','','','','','','','','')

                                                ctx.log.info("insert RESCUTIME_SLICES acct: %s" % acct)

                                                #retval = false
                                                retval = cursor.execute(sql,(stime,etime,acct,app,doc))
                                                #ctx.log.info("insert SLICES: %s" % str(retval))

                                                #outmsg = ''

                                                #ctx.log.info("collect_slice acct: %s" % acct)
                                                #cursor.callproc("collect_slice",(acct,app,doc,stime,etime,outmsg))
                                                #ctx.log.info("collect_slice outmsg: %s" % outmsg)

#CALL "collect_slice"(
#	IN_ACCT => 'e1b9c14f251f9d594546f4a5387f4834'/*<NVARCHAR(32)>*/,
#	IN_APP => 'rescuetime'/*<NVARCHAR(255)>*/,
#	IN_DOC => 'RescueTime'/*<NVARCHAR(255)>*/,
#	IN_VALIDFROM => '2019-07-12 16:13:22'/*<NVARCHAR(24)>*/,
#	IN_VALIDTO => '2019-07-12 16:13:26'/*<NVARCHAR(24)>*/,
#	EX_MESSAGE => ?
#);

                                            cursor.execute("SELECT NOW() FROM DUMMY")
                                            for row in cursor:
                                                ctx.log.info("server time2: %s" % row)

                                            cursor.close()
                                        except:
                                            ctx.log.info("Error connecting to HANA: %s" % "unknown")
                                        #else:
                                        #    ctx.log.info("HANA: %s" % "OK")
                                        finally:
                                            ctx.log.info("HANA: %s" % "Finshed")
                                            conn.close()
                                    else:
                                        ctx.log.info("HDI ENV_VARS NOT SET!")

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
            #tweeked = re.sub(r'.*push_interval: (.*)\n', r'  push_interval: 120\n', tweeked)
            tweeked = re.sub(r'.*push_interval: (.*)\n', r'  push_interval: 60\n', tweeked)
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
