Example: HTTP web server
========================

This is an example for using the RaspberryPi and the CC2500 radio to control the Lelo remote vibrators.

Instructions
------------

Install the required python packages (we use Flask)

```shell
pip install Flask
```

Then on your RaspberryPi launch the server (you will need to be root for this)
```shell
python server.py
```

and finally you can try it from your LAN by calling
```shell
curl http://${RASPBERRY_IP} -X POST --header "Content-Type: application/json" -d @vibe.json
```
