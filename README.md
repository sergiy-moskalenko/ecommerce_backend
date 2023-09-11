<h1 style="text-align: center;">Ecommerce</h1>

---

## Description

---

This is an e-commerce API developed using Django and Django Rest Framework. It offers numerous features, including user
registration, authentication, product list viewing, individual product viewing, view filters for a specific category of
products, order placement, and order viewing. Integration with the LiqPay payment system for secure payment processing.
Additionally, a notification system is implemented to send messages to managers on Telegram when orders are placed.

## Technologies Used

---

- Django
- Django Rest Framework
- PostgreSQL
- Celery
- Rabbitmq
- Redis
- Docker / Docker Compose

## Project setup

---

**NOTE:** The project uses Python 3.10, so need it installed first. It is recommended to
use [pyenv](https://github.com/pyenv/pyenv) for installation.

**NOTE:** Root of the django project is at the ```project``` folder

**NOTE:** If you want payments to work you will need to enter your own LiqPay API keys into the `.env` file (
or [`.env.django`](docker%2Fenv-example%2F.env.django) for docker) in the
settings files. And run ["serveo"](https://serveo.net/).

Here is an instruction on how to set up the project for development:

1. Clone the project:
    ```bash
    git clone https://github.com/MrH3dg3h0g/ecommerce_backend.git
    ```
2. Go to the project directory:
   ```bash
   cd ecommerce_backend
   ``` 
3. Install virtualenv:
   ```bash
   python -m venv venv
   ```
4. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
   To deactivate python virtual environment:
   ```bash
   deactivate
   ```
5. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
6. Add and setup `.env` file:
   ```bash
   cp .env.template .env && nano .env
   ```
7. Switch to postgres (PostgreSQL administrative user) and log into a Postgres session:
    ```bash
   sudo -u postgres psql
   ```
8. Create a database user which we will use to connect to the database:
    ```bash
   CREATE USER ecommerce_usr with password ecommerce_pass;
   ```
9. Create database with name **ecommerce_db**:
    ```bash
   CREATE DATABASE ecommerce_db OWNER ecommerce_usr;
   ```
10. Give our database user access rights to the database we created::
    ```bash
    ALTER ROLE ecommerce_usr WITH CREATEDB;
    ```
11. Exit the SQL prompt and the postgres user's shell session:
    ```bash
    \q 
    ``` 
    then
    ```bash
    exit
    ```
12. Apply migrations:
    ```bash
    python project/manage.py migrate
    ```
13. Create a superuser:
    ```bash
    python project/manage.py createsuperuser
    ```
14. Run the server:
   ```bash
   python project/manage.py runserver
   ```
15. Run the serveo:
    ```bash
    ssh -R 80:localhost:8000 serveo.net
    ```
    Then copy url and paste in `core/settings.py`.

    ![DOMAIN](https://github.com/MrH3dg3h0g/ecommerce_backend/assets/102657228/69b0f9da-b2d0-4ec3-8d06-8f0d9fe3fefd)
16. Download and install: [Redis](https://redis.io/download/), [RabbitMQ](https://www.rabbitmq.com/download.html).

### Use with Docker

---

For local development (from `ecommerce_backend/` directory):

```bash
docker-compose -f docker-compose.yml up -d --build
```

Run log Run the serveo, and copy url, example `https://reverti.serveo.net` then paste in settings.py

```bash
docker logs serveo_web   
```

![DOMAIN](https://github.com/MrH3dg3h0g/ecommerce_backend/assets/102657228/69b0f9da-b2d0-4ec3-8d06-8f0d9fe3fefd)

Create a superuser:

```bash
docker exec -it ecom_web_ctr python manage.py createsuperuser 
```

## Features

___
This e-commerce API offers a wide range of features to enhance the user experience and streamline online shopping:

- **User Registration and Authorization:** Users can register and obtain authorization, allowing them to access various
  features.
- **Category and Product Access:**  Users have access to view categories, products within specific categories, and
  detailed information about specific products, including descriptions, prices, and more.
- **Product Filters:** Users can conveniently view and apply filters specific to a chosen category of products,
  enhancing the product discovery process.
- **Order Placement:**  Each user has the possibility to place an order.
- **Order Viewing:** Authenticated users can access their order history, review past purchases, and track the status of
  their current orders.
- **Secure Payment Processing**: Integration with the LiqPay payment system ensures secure and reliable payment
  processing.
- **Favorites Management:**: Authenticated users can add or remove products to/from their list of favorites for quick
  access and future reference.

## Docs

---
The documentation for the API and the rest of its endpoints are available at:

http://localhost:8000/api/doc/

![Endpoints](https://github.com/MrH3dg3h0g/ecommerce_backend/assets/102657228/2e9f1592-a07a-4bb9-ae48-9ddc60314e1e)