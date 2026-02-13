
import yfinance as yf
import sys

def test_fetch():
    print(f"Python executable: {sys.executable}")
    print(f"yfinance version: {yf.__version__}")
    
    try:
        print("Attempting to fetch Nifty data...")
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="5d")
        
        print(f"Type of hist: {type(hist)}")
        
        if hist is None:
            print("History returned None")
        elif hist.empty:
            print("History is empty DataFrame")
        else:
            print("Successfully fetched Nifty data")
            print(hist.tail())
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fetch()
