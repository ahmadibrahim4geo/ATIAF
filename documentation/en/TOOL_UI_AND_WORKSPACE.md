# Parameters and retained outputs

Sensor/product is first; output folder is LAST. Input Data Folder accepts one scene or a directory containing scenes. Optional manual mapping follows input and reveals native local file/calibration fields; JSON import is optional. QA, optional mosaic, thematic calculation groups, tool-specific advanced options, optional AOI, native projected metre CRS and opt-in map loading follow. Both hosts expose named initially unchecked calculations without search. QGIS uses native group boxes/conditional settings; Pro uses native parameter categories/enabled controls.

Calibration is applied once. QA_PIXEL/SCL and available saturation flags mask invalid pixels. Bands align to the first required band's grid with nearest-neighbour resampling; selected projected metre CRS is applied to the saved raster. This conservative rule is recorded and is not cross-sensor harmonization. Unknown source CRS or unavailable transformations stop; no grid downloads.

Default/equal input destination uses each scene's `Work/Preprocessing_Cache/` and `Results/`. A custom destination creates `<destination>/<scene-folder>/Work` and `Results`. Tools share containers and use immutable run-suffixed filenames. Reruns currently recompute rather than claim an unverified cache hit. Needed intermediate LST may remain. No Results_2. Reports accumulate in `Results/Reports/Runs/` and `Results/Reports/index.html`.

Mosaic requires compatible same-day scenes, retaining individual results/source raster. Temporal currently requires one scene per epoch with matching sensor/level and ordered dates; T2 minus T1. Full/clip are distinct files. Invalid AOI is an error.

Continuous windowed writes use private temporary files. Legacy derived array writers and cumulative index updates need stronger interruption/concurrency validation; complete transactional recovery is not claimed. Map rendering acceptance is separate from saved raster readback.

Spectral results use Results/Spectral_Indices/<category>/<method>/; full and clip products are stored in the same method directory.
