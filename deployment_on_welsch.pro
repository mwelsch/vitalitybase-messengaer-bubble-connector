docker image build -t vb-bubble-connector:alpha01 .
docker run --label-file ./labels \
--restart unless-stopped \
--network web \
--name vb-bubble-connector \
-v /home/moritz/decrypted/vitalitybase-messengaer-bubble-connector:/app \
-d vb-bubble-connector:alpha01
