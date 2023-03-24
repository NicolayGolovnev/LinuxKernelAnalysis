import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
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
    implementation("org.eclipse.jgit:org.eclipse.jgit:4.6.1.201703071140-r")
    implementation("edu.stanford.nlp:stanford-corenlp:4.0.0")
    // new version ??
//    implementation("org.eclipse.jgit:org.eclipse.jgit:5.9.0.202009080501-r")

    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<KotlinCompile>() {
    kotlinOptions.jvmTarget = "11"
}