<?xml version="1.0" encoding="utf-8"?>
<!-- 
Transform to alter the output from heat.exe for Fiji
Main functions:
-Insert the Win64 attribute into all "Component"-elements, not used here, because candle -arch x64 is set.
-Remove the "ImageJ-win64.exe", it is contained in Fiji.wxs
-Set the KeyPath attribute to "no" on the file elements.
Version 1.0, 20200210, Nick Heim, ETHZ, ID-CD
-->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:wix="http://schemas.microsoft.com/wix/2006/wi"
	xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl">

		<!-- Identity Transform, match all elements -->
	<xsl:output method="xml" indent="yes"/>

	<!-- Identity Transform, match all elements (all attributes| any node other than an attribute node and the root node)-->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<!-- Filter out the exe file -->
	<xsl:key name="exe-search" match="wix:Component[contains(wix:File/@Id, 'exe')]" use="@Id" />
	<xsl:template match="wix:Component[key('exe-search', @Id)]" />
	<xsl:template match="wix:ComponentRef[key('exe-search', @Id)]" />

	<!-- Match all the other Files and set the KeyPath attribute to no -->
	<xsl:template match="wix:File" mode="FileKeyPath">
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<!-- <xsl:apply-templates select="@*" /> -->
			<xsl:attribute name="KeyPath">no</xsl:attribute>
			<!-- <xsl:apply-templates select="node()" /> -->
			<xsl:copy-of select="node()" />
		</xsl:copy>
	</xsl:template>

	<!-- Match all the other Components and add the Win64 attribute -->
	<xsl:template match="wix:Component">
		<xsl:copy>
			<xsl:copy-of select="@*"/>
			<!-- Insert the Win64-attribute -->
			<!-- <xsl:attribute name="Win64">yes</xsl:attribute> -->
			<!-- Apply the FileKeyPath template -->
			<xsl:apply-templates mode="FileKeyPath" />
			<!-- Copy the all the other child elements to the output. -->
			<xsl:copy-of select="node()[not(self::wix:File/@KeyPath='yes')]" />
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>
