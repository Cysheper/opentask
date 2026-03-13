from Modules.Log import logging


def main():
    logging.info("OpenTask started successfully.")
    from routers.router import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

