import clerk_backend_api
print(dir(clerk_backend_api))
try:
    from clerk_backend_api import Clerk
    print("Clerk class found")
    print(dir(Clerk))
except ImportError:
    print("Clerk class NOT found")
