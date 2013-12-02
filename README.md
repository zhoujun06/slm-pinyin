usc cs662

main algorithm implemented in convert.py

Data obtained from libgooglepinyin/sunpinyin/chime.

Need 'flask' framework to run the demo website.

Need nginx to setup in front of flask app as a reverse proxy.

Run ./convert.py , the demo cgi will run on port 5000, and nginx will forward the request to this port.

nginx configuration can be found in nginx.conf.

Put index.html in root directory of nginx.

junzhou
