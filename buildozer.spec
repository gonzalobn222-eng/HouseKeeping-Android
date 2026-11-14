[app]
title = HouseKeeping Inspecciones
package.name = housekeeping
package.domain = org.inspecciones
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,xlsx,kv,ttf
version = 0.1
requirements = python3,kivy,openpyxl,pillow,plyer,pyjnius,androidstorage4kivy
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 24
android.accept_sdk_license = True
android.permissions = CAMERA
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
