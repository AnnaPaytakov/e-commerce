# admin panel api:
	users: superuser, staffuser
	CRUD products
	superuser CRUD for staffuser
	stats for per month of products selling
	search , filter products
	websocket receive orders	
	

# client api:
	signup, signin
	one account one device authentication
	List, Retrieve products
	search, filter products
	order products		
	profile get-me, settings


list products from redis cache

update redis cache on CRUD actions

# Technologies used:
	Django/DRF
 	Postgresql
  	Redis
	Websocket (Daphne server)
 	Swagger (api/swagger/)
	Docker