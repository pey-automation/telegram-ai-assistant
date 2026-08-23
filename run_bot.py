print("STEP 1")

from app.routers.telegram import create_bot

print("STEP 2")

application = create_bot()

print("STEP 3")

application.run_polling()

print("STEP 4")