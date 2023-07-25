//
// Copyright 2023 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
////////////////////////////////////////////////////////////////////////

/* ************************************************************************** */
/* ** This file is generated by a script.  Do not edit directly.  Edit     ** */
/* ** defs.py or the (*)Schema.template.cpp files to make changes.         ** */
/* ************************************************************************** */

#include "pxr/imaging/hd/cylinderSchema.h"
#include "pxr/imaging/hd/retainedDataSource.h"

#include "pxr/base/trace/trace.h"


PXR_NAMESPACE_OPEN_SCOPE

TF_DEFINE_PUBLIC_TOKENS(HdCylinderSchemaTokens,
    HDCYLINDER_SCHEMA_TOKENS);



HdDoubleDataSourceHandle
HdCylinderSchema::GetHeight()
{
    return _GetTypedDataSource<HdDoubleDataSource>(
        HdCylinderSchemaTokens->height);
}

HdDoubleDataSourceHandle
HdCylinderSchema::GetRadius()
{
    return _GetTypedDataSource<HdDoubleDataSource>(
        HdCylinderSchemaTokens->radius);
}

HdTokenDataSourceHandle
HdCylinderSchema::GetAxis()
{
    return _GetTypedDataSource<HdTokenDataSource>(
        HdCylinderSchemaTokens->axis);
}

/*static*/
HdContainerDataSourceHandle
HdCylinderSchema::BuildRetained(
        const HdDoubleDataSourceHandle &height,
        const HdDoubleDataSourceHandle &radius,
        const HdTokenDataSourceHandle &axis
)
{
    TfToken names[3];
    HdDataSourceBaseHandle values[3];

    size_t count = 0;
    if (height) {
        names[count] = HdCylinderSchemaTokens->height;
        values[count++] = height;
    }

    if (radius) {
        names[count] = HdCylinderSchemaTokens->radius;
        values[count++] = radius;
    }

    if (axis) {
        names[count] = HdCylinderSchemaTokens->axis;
        values[count++] = axis;
    }

    return HdRetainedContainerDataSource::New(count, names, values);
}

/*static*/
HdCylinderSchema
HdCylinderSchema::GetFromParent(
        const HdContainerDataSourceHandle &fromParentContainer)
{
    return HdCylinderSchema(
        fromParentContainer
        ? HdContainerDataSource::Cast(fromParentContainer->Get(
                HdCylinderSchemaTokens->cylinder))
        : nullptr);
}

/*static*/
const TfToken &
HdCylinderSchema::GetSchemaToken()
{
    return HdCylinderSchemaTokens->cylinder;
} 
/*static*/
const HdDataSourceLocator &
HdCylinderSchema::GetDefaultLocator()
{
    static const HdDataSourceLocator locator(
        HdCylinderSchemaTokens->cylinder
    );
    return locator;
} 
HdCylinderSchema::Builder &
HdCylinderSchema::Builder::SetHeight(
    const HdDoubleDataSourceHandle &height)
{
    _height = height;
    return *this;
}

HdCylinderSchema::Builder &
HdCylinderSchema::Builder::SetRadius(
    const HdDoubleDataSourceHandle &radius)
{
    _radius = radius;
    return *this;
}

HdCylinderSchema::Builder &
HdCylinderSchema::Builder::SetAxis(
    const HdTokenDataSourceHandle &axis)
{
    _axis = axis;
    return *this;
}

HdContainerDataSourceHandle
HdCylinderSchema::Builder::Build()
{
    return HdCylinderSchema::BuildRetained(
        _height,
        _radius,
        _axis
    );
}


PXR_NAMESPACE_CLOSE_SCOPE