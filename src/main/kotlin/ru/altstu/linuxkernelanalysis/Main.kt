package ru.altstu.linuxkernelanalysis

import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.storage.file.FileRepositoryBuilder
import java.io.File
import java.util.*

fun main(args: Array<String>) {
    val repoDir = File("D:\\gimp_for_parse\\gimp\\.git")
    val builder: FileRepositoryBuilder = FileRepositoryBuilder()
        .setGitDir(repoDir)
        .readEnvironment() // scan environment GIT_* variables
        .findGitDir() // scan up the file system tree

    val repo: Repository = builder.build()

    val calendar = Calendar.getInstance()
    calendar.add(Calendar.MONTH, -5)
    val oneMonthAgo = calendar.time

    val scaner = RepositoryScanner(WordMatcher(true), repo, oneMonthAgo,Date(Long.MAX_VALUE))

    val result = scaner.analyze()
    for( r in result){
        println(r.toString())
    }
}