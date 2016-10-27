MUM's Project
============

This is a sample project made with Django to showcase some backend technologies and use cases.

### Requirements
For running this project it is recommend to use [Docker](https://www.docker.com/products/overview) and [Docker Compose](https://docs.docker.com/compose/install/)

### Start the app
Start by cloning this repository:
```
git clone https://github.com/scenting/mums
```

Get into the project
```
cd mums
```

We need to download and create the necessary images, but don't worry, just run:
```
docker-compose build
```

Now we need to create the necessary data into our database
```
docker-compose run --rm web ./manage.py migrate
```

We are now ready to run our app!
It will start on **localhost:8000** so, if you have another application running on that port it will fail
```
docker-compose up
```

That's it, just point your browser to **localhost:8000** and start browsing.


### Notes
As you don't want to sell the same product twice neither hurry your customer, once and order has been placed, the products are reserved, preventing other customers to buy them.
That's why if you load the page while an order is being paid you will see less stock on the initial page.

If the order isn't paid when the timeout expires, the order is canceled and the products are released for other customers to buy them.

There are some discounts applied when you place and order, if you buy a full menu you will get a 20% off and if you get 3 items of the same product you will pay for 2 of them (This only applies to products charged by units).

### Improvements
There is always room for improvements, in this case, the frontend clearly needs some redesign as well as a better way of showing the discounts being applied to each order.

Please feel free to report any issue or comments.
