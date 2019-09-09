# tap_rescuetime
MITM script for tapping rescuetime data

# Run these as the ec2-user to pick up .mtimproxy/config.yaml
mitmproxy -s ./rescuetime.py

mitmproxy --proxyauth mitm:Nirvana8484 -s ./rescuetime.py

mitmproxy -s ./rescuetime.py --proxyauth mitm:Nirvana8484

export HDI_SCHEMA=CONCILE_V0_DEV
export HDI_USER=CONCILE_V0_DEV_AWMSFG3HTXQDCESHJUJGSJ0BI_RT
export HDI_PASS=Qf0Gkt...yr8.ri2pTn46S0l
export HDI_HOST=zeus.hana.prod.us-east-1.whitney.dbaas.ondemand.com
export HDI_PORT=20217
export HDI_CERT="-----BEGIN CERTIFICATE----- MIIDrzCCApegAwI...zAdBgNVHQ4EFgQUA95QNVbR TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw  PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4= -----END CERTIFICATE-----"


echo $HDI_SCHEMA
echo $HDI_USER
echo $HDI_PASS
echo $HDI_HOST
echo $HDI_PORT
echo $HDI_CERT


mitmdump -s ./rescuetime.py


mitmproxy -s ./rescuetime.py


