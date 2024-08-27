#!/bin/bash
#
# SPDX-FileCopyrightText: 2016 The CyanogenMod Project
# SPDX-FileCopyrightText: 2017-2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

set -e

DEVICE=dre
VENDOR=oneplus

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

# If XML files don't have comments before the XML header, use this flag
# Can still be used with broken XML files by using blob_fixup
export TARGET_DISABLE_XML_FIXING=true

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -n | --no-cleanup)
            CLEAN_VENDOR=false
            ;;
        -k | --kang)
            KANG="--kang"
            ;;
        -s | --section)
            SECTION="${2}"
            shift
            CLEAN_VENDOR=false
            ;;
        *)
            SRC="${1}"
            ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        product/etc/sysconfig/com.android.hotwordenrollment.common.util.xml)
            [ "$2" = "" ] && return 0
            sed -i "s/\/my_product/\/product/" "${2}"
            ;;
        system_ext/framework/oplus-ims-ext.jar)
            [ "$2" = "" ] && return 0
            apktool_patch "${2}" "${MY_DIR}/blob-patches/oplus-ims-ext.patch" -r
            ;;
        system_ext/lib64/libwfdnative.so)
            [ "$2" = "" ] && return 0
            sed -i "s/android.hidl.base@1.0.so/libhidlbase.so\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00/" "${2}"
            ;;
        odm/etc/init/android.hardware.drm@1.3-service.widevine.rc)
            [ "$2" = "" ] && return 0
            sed -i "s|writepid /dev/cpuset/foreground/tasks|task_profiles ProcessCapacityHigh|g" "${2}"
            ;;
        vendor/etc/init/android.hardware.neuralnetworks@1.3-service-qti.rc)
            [ "$2" = "" ] && return 0
            sed -i "s|writepid /dev/stune/nnapi-hal/tasks|task_profiles NNApiHALPerformance|g" "${2}"
            ;;
        vendor/etc/init/vendor.qti.media.c2@1.0-service.rc)
            [ "$2" = "" ] && return 0
            sed -i "s|writepid /dev/cpuset/foreground/tasks|task_profiles ProcessCapacityHigh|g" "${2}"
            ;;
        vendor/etc/libnfc-nci.conf)
            [ "$2" = "" ] && return 0
            sed -i "s/NFC_DEBUG_ENABLED=1/NFC_DEBUG_ENABLED=0/" "${2}"
            ;;
        vendor/lib64/hw/com.qti.chi.override.so)
            [ "$2" = "" ] && return 0
            grep -q libcamera_metadata_shim.so "${2}" || "${PATCHELF}" --add-needed libcamera_metadata_shim.so "${2}"
            ;;
        odm/lib64/libCOppLceTonemapAPI.so|odm/lib64/libaps_frame_registration.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --replace-needed "libstdc++.so" "libstdc++_vendor.so" "${2}"
            ;;
        vendor/etc/msm_irqbalance.conf)
            [ "$2" = "" ] && return 0
            sed -i "s/IGNORED_IRQ=19,21,38$/&,209,218/" "${2}"
            ;;
        *)
            return 1
            ;;
    esac

    return 0
}

function blob_fixup_dry() {
    blob_fixup "$1" ""
}

# Initialize the helper
setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" false "${CLEAN_VENDOR}"

extract "${MY_DIR}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"

"${MY_DIR}/setup-makefiles.sh"
