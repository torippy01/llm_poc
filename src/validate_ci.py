from index.create_user_index import test
from utils.utility import set_up


"""
Usage :
python src/validate_ci.py --index-id ??? --context-dir ???
"""



def main():
    set_up()
    test()
    return



if __name__ == "__main__":
    main()