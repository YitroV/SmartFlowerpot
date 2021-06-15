from repositories.Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_historiek():
        sql = "SELECT * FROM historiek"
        return Database.get_rows(sql)

    @staticmethod
    def read_last_record(device_id):
        sql = "SELECT * FROM historiek WHERE DeviceId = %s and datum = (SELECT MAX(datum) FROM historiek WHERE DeviceId = %s)"
        params = [device_id, device_id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_history(id):
        sql = "SELECT * FROM historiek WHERE DeviceId=%s ORDER BY Datum desc limit 100"
        params = [id]
        return Database.get_rows(sql, params)

    @staticmethod
    def create_log_temp_sensor(id, datum, waarde):
        sql = "INSERT INTO historiek (DeviceId, ActieId, Datum, Waarde) VALUES (%s, '3', %s, %s)"
        params = [id, datum, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_log_light_sensor(id, datum, waarde):
        sql = "INSERT INTO historiek (DeviceId, ActieId, Datum, Waarde) VALUES (%s, '2', %s, %s)"
        params = [id, datum, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_log_pump(id, datum, waarde):
        sql = "INSERT INTO historiek (DeviceId, ActieId, Datum, Waarde) VALUES (%s, '1', %s, %s)"
        params = [id, datum, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_log_moisture_sensor(id, datum, waarde):
        sql = "INSERT INTO historiek (DeviceId, ActieId, Datum, Waarde) VALUES (%s, '4', %s, %s)"
        params = [id, datum, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_log_led(id, datum, waarde):
        sql = "INSERT INTO historiek (DeviceId, ActieId, Datum, Waarde) VALUES (%s, '5', %s, %s)"
        params = [id, datum, waarde]
        return Database.execute_sql(sql, params)
