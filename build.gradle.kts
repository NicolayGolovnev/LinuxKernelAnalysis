import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    application
    kotlin("jvm") version "1.8.0"
}

group = "ru.altstu"
version = "1.0-SNAPSHOT"

java.sourceCompatibility = JavaVersion.VERSION_1_8

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
    implementation("org.jetbrains.kotlin:kotlin-reflect")

    implementation("org.eclipse.jgit:org.eclipse.jgit:${property("jgitVersion")}")

    implementation("edu.stanford.nlp:stanford-corenlp:${property("corenlpVersion")}")
    implementation("edu.stanford.nlp:stanford-corenlp:${property("corenlpVersion")}:models")
    implementation("edu.stanford.nlp:stanford-corenlp:${property("corenlpVersion")}:models-english")
    implementation("edu.stanford.nlp:stanford-corenlp:${property("corenlpVersion")}:models-english-kbp")

    testImplementation(kotlin("test"))
}

application {
    mainClass.set("ru.altstu.linuxkernelanalysis.Main")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "11"
}