# otoscrapper
Simple scrapper created to practice async programming

## Setup

0. Run docker-compose:

    ```bash
    docker-compose up
    ```
    or

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Copy the .env.example file as .env:
    ```bash
    cp .env.example .env
    ```

4. Start server:
    ```bash
    python server.py
    ```

## Usage

To populate db:
```bash
curl -X POST localhost:8080/scrap -d '{"brand":"bmw", "model":"x3"}'
```
To list scrapped data:
```bash
curl -X GET -g 'localhost:8080/cars?brand=bmw&model=x3'
```
Additional query parameters:

price[lte], price[gte]