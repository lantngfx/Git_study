# coding: utf8

import torndb
import fire


db_industry = torndb.Connection(host="localhost", user="dever", password="dever", database="user", charset="utf8")

class ImportIndustryData(object):
    """导入新一级行业数据"""
    @classmethod
    def import_new_industry1(cls):
        # 讲一级行业读到列表中
        new_industry_list = list()
        with open("./new_industry1_data", "r") as f:
            for line in f.readlines():
                if line.strip():
                    print type(line.strip())
                    new_industry_list.append([line.strip()])

        db_industry.insertmany("insert into industry_new(industry_name) values (%s)", new_industry_list)


    """导入新二级行业和职位"""
    @classmethod
    def import_new_industry2(cls):
        pass


if __name__ == "__main__":
    """通过fire命令行执行工具来执行程序"""
    fire.Fire(ImportIndustryData)


# cp -P22 import_industry_data.py louyongfeng@123.57.143.47:/home/louyongfeng/hundun_2018/20180901_industry_data_cleaning