An automatic scraper and trader for predictit.org

----
Run
----

In a separate terminal

```
sudo python3 src/predictit/main.py --email {{email}} --password {{password}} --prod
```

----
Test
----

In a separate terminal

```
docker build . --tag zlex7/predictit
docker run -d -p 6379:6379 --name redis redis --appendonly yes
```

then

```
./run-tests.sh
```
