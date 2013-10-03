import threading
import ujson
import time
import copy
import queue


class CollectDaemon(threading.Thread):
    def __init__(self, data_queue):
        self.tmp_filepath = "/tmp/zfs-mon.tmp"
        self.data_queue = data_queue
        self.zfs_data = dict(
            {"ARC": {"HIT": None, "MISS": None},
             "ARCDD": {"HIT": None, "MISS": None},
             "ARCDM": {"HIT": None, "MISS": None},
             "ARCPD": {"HIT": None, "MISS": None},
             "ARCPM": {"HIT": None, "MISS": None},
             "L2": {"HIT": None, "MISS": None},
             "ZFETCH": {"HIT": None, "MISS": None}}
        )

        self.variables = dict(
            {"ARC": {"HIT": "hits", "MISS": "misses"},
            "ARCDD": {"HIT": "demand_data_hits",
                      "MISS": "demand_data_misses"},
            "ARCDM": {"HIT": "demand_metadata_hits",
                      "MISS": "demand_metadata_misses"},
            "ARCPD": {"HIT": "prefetch_data_hits",
                      "MISS": "prefetch_data_misses"},
            "ARCPM": {"HIT": "prefetch_metadata_hits",
                      "MISS": "prefetch_metadata_misses"},
            "L2": {"HIT": "l2_hits", "MISS": "l2_misses"}}
        )

        self.zfetch_variables = dict(
            {"ZFETCH": {"HIT": "hits", "MISS": "misses"}}
        )

        threading.Thread.__init__(self)

    def run(self):
        # Getting initial params of ZFS cache
        initial_zfs_data = copy.deepcopy(self.__get_data())

        while True:
            # sleep 1 sec
            time.sleep(1)
            new_zfs_data = self.__get_data()

            cache_efficiency = dict(
                {"ARC": None,
                 "ARCDD": None,
                 "ARCDM": None,
                 "ARCPD": None,
                 "ARCPM": None,
                 "L2": None,
                 "ZFETCH": None}
            )

            for key in cache_efficiency.keys():
                try:
                    cache_efficiency[key] = round((int(new_zfs_data[key]["HIT"]) -
                                                   int(initial_zfs_data[key]["HIT"])) * 100 /
                                                  (int(new_zfs_data[key]["HIT"]) -
                                                   int(initial_zfs_data[key]["HIT"]) +
                                                   int(new_zfs_data[key]["MISS"]) -
                                                   int(initial_zfs_data[key]["MISS"])))
                except ZeroDivisionError:
                    cache_efficiency[key] = 0

            self.data_queue.put(ujson.dumps(cache_efficiency))
        #print(ujson.dumps(zfs_data))
        #decode_data = ujson.dumps(zfs_data)
        #outfile = open(self.tmp_filepath, "w")
        #try:
        #    outfile.write(decode_data)
        #except Exception as e:
        #    print(str(e))
        #finally:
        #    outfile.close()

    def __get_data(self):
        # Getting params of ZFS cache
        try:
            arcstat = open("/proc/spl/kstat/zfs/arcstats").readlines()
            zfetchstat = open("/proc/spl/kstat/zfs/zfetchstats").readlines()
        except IOError as e:
            print("Hmmm... Maybe you will run this program on "
                  "system without ZFS filesystem. Error message - %s" % str(e))
            exit(1)

        for key, value in self.variables.items():
            self.zfs_data[key]['HIT'] = list(filter(
                lambda x: x.split(' ')[0] == value['HIT'],
                arcstat[2:]))[0].split(' ')[-1].strip()
            self.zfs_data[key]['MISS'] = list(filter(
                lambda x: x.split(' ')[0] == value['MISS'],
                arcstat[2:]))[0].split(' ')[-1].strip()

        for key, value in self.zfetch_variables.items():
            self.zfs_data[key]['HIT'] = list(filter(
                lambda x: x.split(' ')[0] == value['HIT'],
                zfetchstat[2:]))[0].split(' ')[-1].strip()
            self.zfs_data[key]['MISS'] = list(filter(
                lambda x: x.split(' ')[0] == value['MISS'],
                zfetchstat[2:]))[0].split(' ')[-1].strip()

        return self.zfs_data

        #while True:
        #    pass

