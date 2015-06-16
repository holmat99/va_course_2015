import tornado.ioloop
import tornado.web
import os
import pandas as pd
import numpy as np

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_map.html")

class DinoFilter(tornado.web.RequestHandler):
    def get(self):
        self.render("dino_filter.html")

class DinoCheckin(tornado.web.RequestHandler):
    def get(self):
        self.render("stage_map.html")

class FilterData(tornado.web.RequestHandler):
    def get(self):
        x_min = float(self.get_argument("x_min"))
        x_max = float(self.get_argument("x_max"))
        y_min = float(self.get_argument("y_min"))
        y_max = float(self.get_argument("y_max"))
        t_min = np.datetime64(int(self.get_argument("t_min")),"ms")
        t_max = np.datetime64(int(self.get_argument("t_max")),"ms")

        df = self.df
        area = (df["X"]<=x_max) & (df["X"]>=x_min) & (df["Y"]<=y_max) & (df["Y"]>=y_min)
        time = (df["time"] >= t_min) & (df["time"] <= t_max)
        # as int
        guests = sorted(df.loc[area & time,"id"].unique().tolist())
        self.write({"guests" : guests})

    def initialize(self, df):
        self.df = df

class DataHandler(tornado.web.RequestHandler):
    def get(self):
        df = self.df
        guest_id = self.get_argument("id", None)
        if guest_id is None:
            guest_id = np.random.choice(df["id"])
        else:
            guest_id = int(guest_id)
        guest_df = df.loc[df["id"]==guest_id]
        guest_df_list = guest_df.to_dict("records")        
        self.write({"array" :guest_df_list})

    def initialize(self, df):
        self.df = df[["X","Y","id","Timestamp","type"]]


class CheckinHandler(tornado.web.RequestHandler):
    def get(self):
        df= self.df        
        data = df.loc[df["type"] == "check-in"]
        data = data.groupby(['X', 'Y'])['X'].count()
        data = pd.DataFrame(data)
        data.columns = ['veces']
        max_veces = data['veces'].max()
        data['veces'] = abs((data['veces'] / max_veces) - 1)
        #percent_value_include = 0.5
        data.to_csv('C:/Users/Holman/Documents/visualAnalytics/MC1_2015_Data/data1.csv', index=True)   
        data = pd.read_csv("C:/Users/Holman/Documents/visualAnalytics/MC1_2015_Data/data1.csv")
        #percent_value_include_1 = data.sort('veces').get_value(np.int(np.ceil(data.shape[0]*percent_value_include)), 'veces')        
        #data = data.loc[data['veces'] >= percent_value_include_1]
        self.write({"array" :data.to_dict()})
    
    def initialize(self, df):
        #self.df = df[["X","Y","veces"]]
        self.df = df


settings = {"template_path" : os.path.dirname(__file__),
            "static_path" : os.path.join(os.path.dirname(__file__),"static"),
            "debug" : True
            } 

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "C:/Users/Holman/Documents/visualAnalytics/MC1_2015_Data/park-movement-Fri.csv")
    print('loading...')
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df.Timestamp, format="%Y-%m-%d %H:%M:%S")

    
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/data", DataHandler,{"df":df}),
        (r"/data2", CheckinHandler,{"df":df}),
        (r"/checkin", DinoCheckin),
        (r"/filter", DinoFilter),
        (r"/filter_data", FilterData,{"df":df}),
        (r"/static/(.*)", tornado.web.StaticFileHandler,
            {"path": settings["static_path"]})

    ], **settings)
    application.listen(8100)
    print("ready")
    tornado.ioloop.IOLoop.current().start()

