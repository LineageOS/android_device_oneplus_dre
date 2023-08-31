/*
 * Copyright (C) 2022 The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

#include <android-base/logging.h>
#include <android-base/properties.h>

#define _REALLY_INCLUDE_SYS__SYSTEM_PROPERTIES_H_
#include <sys/_system_properties.h>

using android::base::GetProperty;

constexpr const char* BUILD_DESCRIPTION = "OnePlusN200TMO-user 12 SKQ1.210216.001 129f978-4a41b-2f588b release-keys";
constexpr const char* BUILD_FINGERPRINT = "OnePlus/OnePlusN200TMO/OnePlusN200TMO:12/SKQ1.210216.001/R.202308011526:user/release-keys";

constexpr const char* RO_PROP_SOURCES[] = {
    nullptr,
    "bootimage.",
    "odm.",
    "odm_dlkm.",
    "product.",
    "system.",
    "system_dlkm.",
    "system_ext.",
    "vendor.",
    "vendor_dlkm.",
};

/*
 * SetProperty does not allow updating read only properties and as a result
 * does not work for our use case. Write "OverrideProperty" to do practically
 * the same thing as "SetProperty" without this restriction.
 */
void OverrideProperty(const char* name, const char* value) {
    size_t valuelen = strlen(value);

    prop_info* pi = (prop_info*)__system_property_find(name);
    if (pi != nullptr) {
        __system_property_update(pi, value, valuelen);
    } else {
        __system_property_add(name, strlen(name), value, valuelen);
    }
}

void OverrideCarrierProperties() {
    const auto ro_prop_override = [](const char* source, const char* prop, const char* value,
                                     bool product) {
        std::string prop_name = "ro.";

        if (product) prop_name += "product.";
        if (source != nullptr) prop_name += source;
        if (!product) prop_name += "build.";
        prop_name += prop;

        OverrideProperty(prop_name.c_str(), value);
    };

    for (const auto& source : RO_PROP_SOURCES) {
        ro_prop_override(source, "model", "DE2118", true);
        ro_prop_override(source, "device", "OnePlusN200TMO", true);
        ro_prop_override(source, "fingerprint", BUILD_FINGERPRINT, false);
    }
    ro_prop_override(nullptr, "product", "OnePlusN200TMO", false);
    ro_prop_override(nullptr, "description", BUILD_DESCRIPTION, false);
}

/*
 * Only for read-only properties. Properties that can be wrote to more
 * than once should be set in a typical init script (e.g. init.oplus.hw.rc)
 * after the original property has been set.
 */
void vendor_load_properties() {
    //auto device = GetProperty("ro.product.product.device", "");
    auto prj_codename = GetProperty("ro.boot.project_codename", "");

    // T-Mobile (dre8t) or Metro by T-Mobile (dre8m)
    if (prj_codename != "dre9")
        OverrideCarrierProperties();
}
