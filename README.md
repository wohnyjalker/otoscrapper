# otoscrapper
Simple scrapper created to practice async programming

## Setup

### Using docker-compose

1. Copy the .env.example file as .env:
   ```bash
    cp .env.example .env
    ```

2. Run docker-compose:
    ```bash
    docker-compose up
    ```
   
### Without docker-compose

1. Copy the .env.example file as .env:
   ```bash
    cp .env.example .env
    ```
   
2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   ```
   
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
   
4. Copy the .env.example file as .env:
    ```bash
    cp .env.example .env
    ```

5. Start server:
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