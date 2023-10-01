#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/oneplus/dre',
    'hardware/oplus',
    'hardware/qcom-caf/common/libqti-perfd-client',
    'hardware/qcom-caf/sm8350',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_vendor' if partition in ['odm', 'vendor'] else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.fm@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'odm/etc/init/android.hardware.drm@1.3-service.widevine.rc': blob_fixup()
        .regex_replace('writepid /dev/cpuset/foreground/tasks', 'task_profiles ProcessCapacityHigh'),
    ('odm/lib/liblvimfs_wrapper.so', 'odm/lib64/libCOppLceTonemapAPI.so', 'odm/lib64/libaps_frame_registration.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    'odm/lib64/libarcsoft_portrait_super_night_raw.so': blob_fixup()
        .clear_symbol_version('remote_handle_close')
        .clear_symbol_version('remote_handle_invoke')
        .clear_symbol_version('remote_handle_open')
        .clear_symbol_version('remote_handle64_close')
        .clear_symbol_version('remote_handle64_invoke')
        .clear_symbol_version('remote_handle64_open')
        .clear_symbol_version('remote_register_buf_attr')
        .clear_symbol_version('remote_register_buf')
        .clear_symbol_version('rpcmem_alloc')
        .clear_symbol_version('rpcmem_free')
        .clear_symbol_version('rpcmem_to_fd'),
    'odm/lib64/libOGLManager.so': blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('odm/lib64/libwvhidl.so','odm/lib64/mediadrm/libwvdrmengine.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    'product/etc/sysconfig/com.android.hotwordenrollment.common.util.xml': blob_fixup()
        .regex_replace('/my_product', '/product'),
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .add_needed('libinput_shim.so'),
    'vendor/bin/init.kernel.post_boot-blair.sh': blob_fixup()
        .patch_file('blob-patches/init-post-boot-blair.patch'),
    'vendor/bin/init.kernel.post_boot-holi.sh': blob_fixup()
        .patch_file('blob-patches/init-post-boot-holi.patch'),
    'vendor/etc/init/vendor.qti.media.c2@1.0-service.rc': blob_fixup()
        .regex_replace('writepid /dev/cpuset/foreground/tasks', 'task_profiles ProcessCapacityHigh'),
    ('vendor/etc/media_codecs.xml','vendor/etc/media_codecs_blair.xml','vendor/etc/media_codecs_blair_lite.xml','vendor/etc/media_codecs_holi.xml'): blob_fixup()
        .regex_replace('\n    <Include href="media_codecs_google_audio.xml" />', '')
        .regex_replace('\n    <Include href="media_codecs_vendor_audio.xml" />', '')
        .regex_replace('\n    <Include href="media_codecs_google_telephony.xml" />', '')
        .regex_replace('\n    <Include href="media_codecs_google_c2.xml" />', '')
        .regex_replace('\n    <Include href="media_codecs_c2_audio.xml" />', '')
        .regex_replace('\n        <Setting name="max-video-encoder-input-buffers" value="11" />', '\n        <Domain name="telephony" enabled="true" />\n        <Setting name="max-video-encoder-input-buffers" value="11" />'),
    'vendor/etc/media_holi/video_system_specs.json': blob_fixup()
        .regex_replace('"max_retry_alloc_output_timeout": 2000,', '"max_retry_alloc_output_timeout": 0,'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/msm_irqbalance.conf': blob_fixup()
        .regex_replace('IGNORED_IRQ=19,21,38$', 'IGNORED_IRQ=19,21,38,209,218'),
    'vendor/etc/public.libraries.txt': blob_fixup()
        .regex_replace('libqti-perfd-client.so\n', ''),
    'vendor/etc/qdcm_calib_data_nt36672c_tm_fhd_plus_video_mode_dsi_panel.xml': blob_fixup()
        .regex_replace('FeatureType="2" Disable="false"', 'FeatureType="2" Disable="true"')
        .regex_replace('FeatureType="7" Disable="false"', 'FeatureType="7" Disable="true"')
        .regex_replace('FeatureType="8" Disable="false"', 'FeatureType="8" Disable="true"')
        .regex_replace('20121_v1_20201113', 'native')
        .regex_replace('SRGB', 'sRGB'),
    'vendor/lib64/hw/com.qti.chi.override.so': blob_fixup()
        .add_needed('libcamera_metadata_shim.so'),
    (
        'vendor/lib64/libdpps.so',
        'vendor/lib64/libsnapdragoncolor-manager.so',
    ): blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'dre',
    'oneplus',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
