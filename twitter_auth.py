import os
import webbrowser
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")

# OAuth 2.0 settings
CALLBACK_URL = "https://127.0.0.1:8000/callback"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback"""
        try:
            # Parse the callback URL
            query_components = parse_qs(urlparse(self.path).query)
            
            if "code" in query_components:
                # Get the authorization code
                auth_code = query_components["code"][0]
                
                # Exchange code for tokens
                oauth2_user_handler = tweepy.OAuth2UserHandler(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    redirect_uri=CALLBACK_URL,
                    scope=SCOPES
                )
                
                # Get access token
                access_token = oauth2_user_handler.fetch_token(auth_code)
                
                # Send success response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Display tokens
                response = f"""
                <html>
                <body>
                <h1>Authentication Successful!</h1>
                <p>Add these tokens to your .env file:</p>
                <pre>
                TWITTER_ACCESS_TOKEN={access_token["access_token"]}
                TWITTER_REFRESH_TOKEN={access_token["refresh_token"]}
                </pre>
                <p>You can close this window now.</p>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                
                # Store tokens globally for the main script to access
                self.server.access_token = access_token
                
            else:
                # Handle error
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Error: No authorization code received")
                
        except Exception as e:
            # Handle error
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass

def create_self_signed_cert():
    """Create a self-signed certificate for HTTPS"""
    from OpenSSL import crypto
    from datetime import datetime, timedelta
    
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().CN = "127.0.0.1"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Save certificate and private key
    with open("server.crt", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("server.key", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

def main():
    """Main function to handle Twitter OAuth 2.0 authentication"""
    if not all([CLIENT_ID, CLIENT_SECRET]):
        print("Error: TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET must be set in .env file")
        return
    
    print("\n=== Twitter OAuth 2.0 Authentication ===")
    print("\nThis script will help you obtain OAuth 2.0 tokens for Twitter API v2.")
    
    try:
        # Create self-signed certificate
        print("\nCreating self-signed certificate...")
        create_self_signed_cert()
        
        # Initialize OAuth 2.0 handler
        oauth2_user_handler = tweepy.OAuth2UserHandler(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=CALLBACK_URL,
            scope=SCOPES
        )
        
        # Get authorization URL
        auth_url = oauth2_user_handler.get_authorization_url()
        
        print("\nStarting local HTTPS server to handle callback...")
        server = HTTPServer(("127.0.0.1", 8000), CallbackHandler)
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        
        # Wrap socket with SSL context
        server.socket = context.wrap_socket(server.socket, server_side=True)
        
        print("\nOpening browser for authentication...")
        webbrowser.open(auth_url)
        
        print("\nWaiting for callback...")
        server.handle_request()
        
        if hasattr(server, "access_token"):
            print("\n✅ Authentication successful!")
            print("\nAdd these tokens to your .env file:")
            print(f"TWITTER_ACCESS_TOKEN={server.access_token['access_token']}")
            print(f"TWITTER_REFRESH_TOKEN={server.access_token['refresh_token']}")
        else:
            print("\n❌ Authentication failed: No tokens received")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    finally:
        # Clean up certificate files
        try:
            os.remove("server.crt")
            os.remove("server.key")
        except:
            pass
        print("\nYou can close this window now.")

if __name__ == "__main__":
    main()