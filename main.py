import mission
from mission import utils
import pytplot

def main():
    time_range = ['2013-06-01','2013-06-02']
    probe = 'a'
#    id = 'l3%pa'
#    files = mission.rbsp.hope.load_file(time_range, probe, id)
#    ids = ['l2%e_hires_uvw','l2%vsvy_hires','l2%e_spinfit_mgse','l2%spec','l2%fbk','l2%esvy_despun','l3']
    time_range = ['2013-06-07/04:30','2013-06-07/05:00']
    ids = ['l1%vb1-split','l1%mscb1-split','l1%vsvy','l1%esvy']

    time_range = ['2013-04-25','2013-04-26']
    ids = ['l1%eb2','l1%vb2','l1%mscb2']

    time_range = ['2012-10-11','2012-10-12']
    ids = ['l1%vb1','l1%eb1','l1%mscb1']

    files = list()
    for id in ids:
        files.append(mission.rbsp.efw.load_file(time_range, probe, id))
    print(files)


if __name__ == '__main__':
    main()