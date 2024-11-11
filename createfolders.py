import os

variables = [10, 50, 250]
avg_deg = [2, 4, 12]
sample = [40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
st_type = ['ER', 'SF']


os.makedirs('Data', exist_ok=True)


for st in st_type:

    os.makedirs(f"Data/{st}", exist_ok=True)
    

    for var in variables:
        var_dir = f"Data/{st}/Variable_{var}"
        os.makedirs(var_dir, exist_ok=True)
        

        for ad in avg_deg:

            ad_dir = f"{var_dir}/AD_{ad}"
            os.makedirs(ad_dir, exist_ok=True)
            
 
            for n in sample:
                n_dir = f"{ad_dir}/n_{n}"
                os.makedirs(n_dir, exist_ok=True)


