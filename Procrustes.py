import os
import glob
import json
import numpy as np
import pandas as pd
from scipy.spatial import procrustes

class Procrustes:
    def __init__(self, title, perplexity, iteration, learning_rate):
        self.title = title
        self.perplexity = perplexity
        self.iteration = iteration
        self.learning_rate = learning_rate
        
        self.embeddings = []
        self.data = []
        self.data_len = None
    
    
    """
    embedded_data = pd.read_csv(file)
            hpram = file[file.rfind("/")+1:file.rfind(".")]
            hpram = hpram.split('_')
            self.data.append(
                {
                    "Hyperparameter": 
                        {
                            "init" : hpram[hpram.index('init')+1],
                            "perplexity": hpram[hpram.index('perp')+1],
                            "max_iteration": hpram[hpram.index('iter')+1],
                            "learning_rate": hpram[hpram.index('lr')+1]
                        },
                    "Points":
                        {
                            "idx": [i for i in range(len(embedded_data))],
                            "0": embedded_data["0"].tolist(),
                            "1": embedded_data["1"].tolist(),
                            "class": ("None" if "class" not in embedded_data.columns else embedded_data["class"].tolist())
                        }
                }
            )
    """
    
    def load_files(self):
        if self.learning_rate == -1:
            self.learning_rate = "auto"
        self.path = f'/home/myeongwon/mw_dir/Ensemble_DR/Ensemble_DR/static/result/{self.title}/perplexity_{self.perplexity}_max_iter_{self.iteration}_learning_rate_{self.learning_rate}_'

        self.csv_files = glob.glob(self.path+"/*.csv")

        for file in self.csv_files:           
            embedded_data = pd.read_csv(file)
            self.data_len = len(embedded_data)
            hpram = file[file.rfind("/")+1:file.rfind(".")]
            hpram = hpram.split('_')
            self.data.append(
                {
                    "Hyperparameter": 
                        {
                            "init" : hpram[hpram.index('init')+1],
                            "perplexity": hpram[hpram.index('perp')+1],
                            "max_iteration": hpram[hpram.index('iter')+1],
                            "learning_rate": hpram[hpram.index('lr')+1]
                        }
                }
            )
            self.embeddings.append(
                {
                    "idx": [i for i in range(len(embedded_data))],
                    "0": embedded_data["0"].tolist(),
                    "1": embedded_data["1"].tolist(),
                    "class": (["None" for _ in range(len(embedded_data))] if "class" not in embedded_data.columns else embedded_data["class"].tolist())
                }
            )

    def translation_and_scaling(self):
        for d in self.embeddings:
            x, y= np.array(d["0"]), np.array(d["1"])
            
            x = x - x.mean()
            y = y - y.mean()

            s = x**2 + y**2
            s = np.sqrt(s.sum()/len(x))
            x /= s
            y /= s

            d["Points"]["0"] = list(x)
            d["Points"]["1"] = list(y)
            
    def Procrustes(self):
        mtx1 = np.stack((np.array(self.embeddings[0]["0"]), np.array(self.embeddings[0]["1"])), axis=1)

        for i, d in enumerate(self.embeddings):
            if i == 0:
                continue
            mtx2 = np.stack((np.array(d["0"]), np.array(d["1"])), axis=1)
            mtx1, mtx2, disparity = procrustes(mtx1, mtx2)
    
            mtx2 = mtx2.T
            d["0"] = list(mtx2[0])
            d["1"] = list(mtx2[1])

        mtx1 = mtx1.T
        self.embeddings[0]["0"] = list(mtx1[0])
        self.embeddings[0]["1"] = list(mtx1[1])

    def save_result(self):
        for i, d in enumerate(self.data):
            d["Embeddings"] = [
                {
                    "idx": j,
                    "0": self.embeddings[i]["0"][j],
                    "1": self.embeddings[i]["1"][j],
                    "class": self.embeddings[i]["class"][j]
                } for j in range(self.data_len)
            ]     
        result = {"DR": self.data}
        
        with open(self.path+"/result.json", "w") as json_file:
            json.dump(result, json_file, indent="\t")
        
        return result



    def run(self):
        self.load_files()
        self.Procrustes()
        return self.save_result()



"""
let [x, y] = [0, 0];
datum.forEach((d) => {
x += d["0"];
y += d["1"];
});
x /= datum.length;
y /= datum.length;

datum.forEach((d) => {
d["0"] -= x;
d["1"] -= y;
});

return datum;
"""
