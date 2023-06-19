import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# Note: Needs to run on Python 3.9, with Cartopy installed manually

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # Other options are possible, e.g. Geodetic
ax.stock_img()


# All AWS locations used:
cali_lon, cali_lat = -122.4, 37.774
mtl_lon, mtl_lat = -73.58781, 45.50884
saop_lon, saop_lat = -46.63611, -23.5475 
frank_lon, frank_lat = 8.68417, 50.11552 
singa_lon, singa_lat = 103.8454093, 1.3146631 
mumbai_lon, mumbai_lat = 72.88261, 19.07283 
seoul_lon, seoul_lat = 126.9784, 37.566
capetown_lon, capetown_lat = 18.423, -33.925
bahrain_lon, bahrain_lat = 50.6014985, 25.9434256 
sydney_lon, sydney_lat =  151.20732, -33.86785
melbourne_lon, melbourne_lat = 144.96332, -37.814
stockholm_lon, stockholm_lat = 18.0649, 59.33258
ohio_lon, ohio_lat =  -87.65005, 41.85003
oregon_lon, oregon_lat =  -122.33207, 47.60621
hongkong_lon, hongkong_lat = 114.15769, 22.28552
tokyo_lon, tokyo_lat = 139.69171, 35.6895 
jakarta_lon, jakarta_lat = 106.84513, -6.21462
london_lon, london_lat = -0.12574, 51.50853 
paris_lon, paris_lat = 2.3488, 48.85341
virginia_lon, virginia_lat = -77.03637, 38.89511 
zurich_lon, zurich_lat = 8.55, 47.36667  


far = ( 
        [stockholm_lon, stockholm_lat],
        [capetown_lon, capetown_lat],
        [saop_lon, saop_lat],
        [sydney_lon, sydney_lat],
        )


spread = ( 
        [cali_lon, cali_lat], 
        [cali_lon+2, cali_lat+2], 
        [mtl_lon, mtl_lat],
        [ohio_lon, ohio_lat], 
        [ohio_lon+2, ohio_lat+2], 
        [oregon_lon, oregon_lat], 
        [virginia_lon, virginia_lat],
        [stockholm_lon, stockholm_lat],
        [paris_lon, paris_lat],
        [frank_lon, frank_lat],
        [london_lon, london_lat],
        [zurich_lon, zurich_lat],
        [zurich_lon+2, zurich_lat+2],
        [sydney_lon, sydney_lat],
        [seoul_lon, seoul_lat], 
        [singa_lon, singa_lat],
        )

all = ( [cali_lon, cali_lat], 
        [mtl_lon, mtl_lat],
        [tokyo_lon, tokyo_lat], 
        [frank_lon, frank_lat],
        [singa_lon, singa_lat], 
        [mumbai_lon, mumbai_lat],
        [seoul_lon, seoul_lat], 
        [jakarta_lon, jakarta_lat],
        [bahrain_lon, bahrain_lat],
        [paris_lon, paris_lat],
        [ohio_lon, ohio_lat], 
        [london_lon, london_lat],
        [oregon_lon, oregon_lat], 
        [hongkong_lon, hongkong_lat],
        [virginia_lon, virginia_lat],
        [ohio_lon-1, ohio_lat-1],
        )


for loc in all:
    plt.plot(loc[0], loc[1], 'o', color = 'red', ms=10, transform=ccrs.PlateCarree())
    
    #plt.text(loc[0] - 3, loc[1] - 12, 'λ = 1.21, σ = 0.89',
    #        horizontalalignment='left', transform=ccrs.PlateCarree())

plt.savefig('map.png')
plt.show()



