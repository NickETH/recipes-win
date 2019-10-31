<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe for Mozilla Firefox
Good for Firefox x64 57.x and newer
Main functions:
Preserve the GUID for components, which existed in previous versions
Insert the Win64 attribute into all "Component"-elements
Correct the "'Accessible.tlb'-Component" to compile smoothely
Version 1.0, 20171124, Nick Heim, ETHZ, ID-MS
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
			<!-- Insert the Win64-attribute -->
			<xsl:attribute name="Win64">yes</xsl:attribute>
			<!-- Copy the child elements from the new Component. -->
			<xsl:copy-of select="node()" />
		</xsl:copy>
	</xsl:template>
	
	<!-- Match Component 'Accessible.tlb' which needs to be altered deeper. It uses also in Snapshot.xml, and use the snapshot version -->
	<xsl:template match="wix:Component[@Id='Accessible.tlb']">
		<xsl:variable name="component" select="."/>
		<!-- Get the Component-element from Snapshot.xml -->
		<xsl:variable name="oldcomp" select="document('Snapshot.xml')//wix:Component[@Id = $component/@Id]"/>
		<xsl:variable name="typelibvar" select="wix:TypeLib[@Id[contains(., 'B4D37CDA-0DAC-45E6-B613-158A5EB94293')]]"/>

	  	<xsl:copy>
			<!-- Copy the ID-attribute from the new Component. -->
			<xsl:copy-of select="$component/@Id"/>
			<!-- Copy the Guid-attribute from the matching Component in Snapshot.xml -->
			<xsl:copy-of select="$oldcomp/@Guid"/>
			<!-- Insert the Win64-attribute -->
			<xsl:attribute name="Win64">yes</xsl:attribute>
			<!-- Create a new File element, because we need to nest the 2 nodes at the bottom and insert the attributes from the old one -->
			<xsl:element name="File" namespace="http://schemas.microsoft.com/wix/2006/wi">
				<xsl:attribute name="Id">
					<xsl:value-of select="wix:File[@Id='Accessible.tlb']/@Id" />
				</xsl:attribute>
				<xsl:attribute name="KeyPath">
					<xsl:value-of select="wix:File[@Id='Accessible.tlb']/@KeyPath" />
				</xsl:attribute>
				<xsl:attribute name="Source">
					<xsl:value-of select="wix:File[@Id='Accessible.tlb']/@Source" />
				</xsl:attribute>
				<!-- Create a new TypeLib element, because we need to make it a child of File and insert the Language attribute -->
				<xsl:element name="TypeLib" namespace="http://schemas.microsoft.com/wix/2006/wi">
					<xsl:attribute name="Id">
						<xsl:value-of select="$typelibvar/@Id" />
					</xsl:attribute>
					<xsl:attribute name="Description">
						<xsl:value-of select="$typelibvar/@Description" />
					</xsl:attribute>
					<xsl:attribute name="HelpDirectory">
						<xsl:value-of select="$typelibvar/@HelpDirectory" />
					</xsl:attribute>
					<xsl:attribute name="MajorVersion">
						<xsl:value-of select="$typelibvar/@MajorVersion" />
					</xsl:attribute>
					<xsl:attribute name="MinorVersion">
						<xsl:value-of select="$typelibvar/@MinorVersion" />
					</xsl:attribute>
					<xsl:attribute name="Language">0</xsl:attribute>
				</xsl:element>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	
	<!-- Match all the other Components and add the Win64 attribute -->
	<xsl:template match="wix:Component">
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<!-- Insert the Win64-attribute -->
			<xsl:attribute name="Win64">yes</xsl:attribute>
			<!-- Copy the child elements from the new Component. -->
			<xsl:copy-of select="node()" />
		</xsl:copy>
	</xsl:template>
	
</xsl:stylesheet>
