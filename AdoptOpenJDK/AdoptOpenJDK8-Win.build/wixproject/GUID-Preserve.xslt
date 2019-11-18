<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe for Mozilla Firefox
Good for Firefox x86 57.x and newer
Main functions:
Preserve the GUID for components, which existed in previous versions
Version 1.0, 20171126, Nick Heim, ETHZ, ID-MS
-->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:wix="http://schemas.microsoft.com/wix/2006/wi"
	xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl">

		<!-- Identity Transform, match all elements -->
	<xsl:output method="xml" indent="yes"/>

	<!-- Identity Transform, match all elements -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<!-- Set up keys of component Ids from Snapshot.xml -->
	<xsl:key name="snapshot-search" match="wix:Component[@Id = document('Snapshot.xml')//wix:Component/@Id]" use="@Id"/>

	<!-- Match Components that also exist in Snapshot.xml, and use the GUID from the snapshot version -->
	<xsl:template match="wix:Component[key('snapshot-search', @Id)]">
		<xsl:variable name="component" select="."/>
		<!-- Get the Component-element from Snapshot.xml -->
		<xsl:variable name="oldcomp" select="document('Snapshot.xml')//wix:Component[@Id = $component/@Id]"/>

		<xsl:copy>
			<!-- Copy the ID-attribute from the new Component. -->
			<xsl:copy-of select="$component/@Id"/>
			<!-- Copy the Guid-attribute from the matching Component in Snapshot.xml -->
			<!-- <xsl:copy-of select="document('Snapshot.xml')//wix:Component[@Id = $component/@Id]/@Guid"/> -->
			<xsl:copy-of select="$oldcomp/@Guid"/>
			<!-- Copy the child elements from the new Component. -->
			<xsl:copy-of select="node()" />
		</xsl:copy>
	</xsl:template>

	<!-- Match Component 'AccessibleHandler.dll' which needs to be altered deeper. It uses also in Snapshot.xml, and use the snapshot version -->
	<xsl:template match="wix:Component[@Id='AccessibleHandler.dll']">
		<xsl:variable name="component" select="."/>
		<!-- Get the Component-element from Snapshot.xml -->
		<xsl:variable name="oldcomp" select="document('Snapshot.xml')//wix:Component[@Id = $component/@Id]"/>
		<!-- Get the Class-element from this file -->
		<xsl:variable name="classvar" select="wix:Class[@Id[contains(., '1BAA303D-B4B9-45E5-9CCB-E3FCA3E274B6')]]"/>
		<xsl:variable name="classvar2" select="wix:File/wix:Class[@Id[contains(., 'DCA8D857-1A63-4045-8F36-8809EB093D04')]]"/>
	  	<xsl:copy>
			<!-- Copy the ID-attribute from the new Component. -->
			<xsl:copy-of select="$component/@Id"/>
			<!-- Copy the Guid-attribute from the matching Component in Snapshot.xml -->
			<xsl:copy-of select="$oldcomp/@Guid"/>
			<!-- Insert the Win64-attribute -->
			<!-- Create a new File element, because we need to nest the 2 nodes at the bottom and insert the attributes from the old one -->
			<xsl:element name="File" namespace="http://schemas.microsoft.com/wix/2006/wi">
				<xsl:attribute name="Id">
					<xsl:value-of select="wix:File[@Id='AccessibleHandler.dll']/@Id" />
				</xsl:attribute>
				<xsl:attribute name="KeyPath">
					<xsl:value-of select="wix:File[@Id='AccessibleHandler.dll']/@KeyPath" />
				</xsl:attribute>
				<xsl:attribute name="Source">
					<xsl:value-of select="wix:File[@Id='AccessibleHandler.dll']/@Source" />
				</xsl:attribute>
				<!-- Create a new Class element, because we need to make it a child of File and insert the Language attribute -->
				<!-- <Class Id="{DCA8D857-1A63-4045-8F36-8809EB093D04}" Context="InprocServer32" Description="PSFactoryBuffer" ThreadingModel="both" /> -->
				<xsl:element name="Class" namespace="http://schemas.microsoft.com/wix/2006/wi">
					<xsl:attribute name="Id">
						<xsl:value-of select="$classvar2/@Id" />
					</xsl:attribute>
					<xsl:attribute name="Context">
						<xsl:value-of select="$classvar2/@Context" />
					</xsl:attribute>
					<xsl:attribute name="Description">
						<xsl:value-of select="$classvar2/@Description" />
					</xsl:attribute>
					<xsl:attribute name="ThreadingModel">
						<xsl:value-of select="$classvar2/@ThreadingModel" />
					</xsl:attribute>
				</xsl:element>

				<!-- Create a new Class element, because we need to make it a child of File and insert the Language attribute -->
				<xsl:element name="Class" namespace="http://schemas.microsoft.com/wix/2006/wi">
					<xsl:attribute name="Id">
						<xsl:value-of select="$classvar/@Id" />
					</xsl:attribute>
					<xsl:attribute name="Handler">
						<xsl:value-of select="$classvar/@Handler" />
					</xsl:attribute>
				</xsl:element>
			</xsl:element>
			<xsl:copy-of select="wix:Interface|wix:RegistryValue" />
		</xsl:copy>
	</xsl:template>
	
</xsl:stylesheet>
