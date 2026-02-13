
import yfinance as yf

def test_fetch():
    try:
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="5d")
        if not hist.empty:
            print("Successfully fetched Nifty data")
            print(hist.tail())
        else:
            print("Fetched empty dataframe")
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    test_fetch()
