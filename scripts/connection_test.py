# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
#
# load_dotenv()
# url = os.getenv("POSTGRES_URL")
# print(f"Testing URL: {url}")
#
# try:
#     engine = create_engine(url)
#     with engine.connect() as conn:
#         print("Connection success!")
# except Exception as e:
#     print(f"ERROR: {e}")