# Plan

## 01 - http server and http client
* run local http server
* create client

## 02 - add socks proxy between with socketserver
* create socks server
* change client
* discuss about "what if need to change this to asyncio?"

## 03 - refactor to asyncio
* refactor socks server
* discuss about "what if need to change to strictly different"
	* callback-based solution (asyncio protocol/transport)
	* generator based solution

## 04 - refactor to sans-io socks
* refactor socks server

## 05 - sans-io structured
* show no difference with classic functions
* why it is better than io-interface?
	* async/sync worlds
	* testing
	* io-call localization
