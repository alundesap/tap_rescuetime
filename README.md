# tap_rescuetime
MITM script for tapping rescuetime data

# Run these as the ec2-user to pick up .mtimproxy/config.yaml
mitmproxy -s ./rescuetime.py

mitmproxy --proxyauth mitm:Nirvana8484 -s ./rescuetime.py

mitmproxy -s ./rescuetime.py --proxyauth mitm:Nirvana8484

export HDI_SCHEMA=CONCILETIME_V0_DEV
export HDI_USER=CONCILETIME_V0_DEV_1VJYS3NCO3WPGNM3R23CZZHON_RT
export HDI_PASS=Ac8KJnQdsmYzrj9N3LvibAF3QCUtvaL4NH-fs-GpMfENJxzp7.7zdp0maMlCYEbHtx7WHa96jNKttqWjn8qbAHI6zoAXxu24QitNNlpD4OvuYhsaoRunGVMxg0DkVRDQ
export HDI_HOST=parvus.lcfx.net
export HDI_PORT=30015
mitmdump -s ./rescuetime.py

