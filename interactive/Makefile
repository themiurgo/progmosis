all:
	ogr2ogr -f GeoJSON data/senegal.json data/senegal_arr_2014_wgs.shp
	topojson -o data/senegal-topo.json --id-property ARR -- data/senegal.json
