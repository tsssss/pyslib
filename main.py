import mission
from mission import rbsp
from mission.rbsp import RBSP

def main():
    time_range = ['2013-06-01','2013-06-02']
    probe = 'a'
    id = 'l3%mom'

    hope = RBSP.HOPE(time_range, probe)
    files = hope.load_file(id)
    print(files)

#    vars = ['']
#    hope.load_vars(vars)

if __name__ == '__main__':
    main()