import mission

def main():
    time_range = ['2013-06-01','2013-06-02']
    probe = 'a'
    id = 'l3%mom'
    files = mission.rbsp.hope(time_range, probe, id)

    print(files)

if __name__ == '__main__':
    main()