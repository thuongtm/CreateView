# This Python file uses the following encoding: utf-8
import os, sys
from bs4 import BeautifulSoup
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import oracledb
import pandas as pd
import ModuleSecurity


class Connect:
    def __init__(self, connect=None):
        try:
            oracledb.version = "8.3.0"
            sys.modules["cx_Oracle"] = oracledb
            oracledb.init_oracle_client(
                lib_dir=r"c:\oracle\instantclient_21_14"
            )
            if connect == None:
                try:
                    self.read_config()
                except Exception as e:
                    raise FileExistsError(
                        "Do not Find or Read file xml."
                        + str(
                            e.args,
                        )
                    )
            else:
                self.server = connect.server
                self.password = connect.password
                self.port = connect.port
                self.connect_dwh = connect.connect_dwh
                self.user = connect.user
                self.db = connect.db
        except:
            raise

    def read_config(self):
        link_file_config = str(os.getcwd()) + "\\config.xml"
        try:
            with open(link_file_config, "r") as configFile:
                config = configFile.read()
                c = ModuleSecurity.Security()
                bs_data = BeautifulSoup(config, "xml")
                bs_info_dwh = c.decrypt(bs_data.find("dwh").getText())
                (self.server, self.port, self.user, self.password, self.db) = (
                    bs_info_dwh.split(";")
                )
                self.connect_dwh = f"oracle+oracledb://{self.user}:{self.password}@{self.server}:{self.port}/?service_name={self.db}"
        except:
            raise

    def check_connect(self):
        try:
            connect = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
        except:
            raise

    def get_data_operation(self, sql):
        try:
            self.check_connect()
            connect_engine = create_engine(self.connect_dwh)
            connect = connect_engine.connect()
            data = pd.DataFrame()
            data = pd.read_sql(sql=text(sql), con=connect)
            return data
        except:
            raise
        finally:
            connect.close()

    def excute_query(self, sql):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.execute(sql)
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def excute_query_test(self, sql):
        connection = oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=f"{self.server}/{self.db}",
        )
        cursors = connection.cursor()
        cursors.execute(sql)
        cursors.close()
        connection.close()

    def insert_view_line_column(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_column_insert",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_header_view(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            newViewNo = cursors.callfunc(
                "t_func_view_insert",
                parameters=parameter,
                return_type=int,
            )
            return newViewNo
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_view_line_column(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_column_insert",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_view_line_column_new(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_column_new_insert",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_view_line_sort(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_sort_insert",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_view_line_filter(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_filter_insert",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_header_view(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_update",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_view_line_column(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_column_update",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_view_line_column_new(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_column_new_update",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_view_line_sort(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_sort_update",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_view_line_filter(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_filter_update",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def delete_header_view(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_delete",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def update_view_release_status(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_update_view_release",
                parameters=parameter,
            )
        except:
            raise
        finally:
            cursors.close()
            connection.close()

    def insert_log_login(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_login_log",
                parameters=parameter,
            )
        except:
            pass
        finally:
            cursors.close()
            connection.close()

    def insert_log_transaction(self, parameter):
        try:
            connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=f"{self.server}/{self.db}",
            )
            cursors = connection.cursor()
            cursors.callproc(
                "t_proc_view_log_transaction",
                parameters=parameter,
            )
        except:
            pass
        finally:
            cursors.close()
            connection.close()
