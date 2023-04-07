package ru.altstu.linuxkernelanalysis
import me.tongfei.progressbar.ProgressBar
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.lib.Constants
import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import java.util.*
import java.util.concurrent.ForkJoinPool
import kotlin.concurrent.thread


class RepositoryScanner(
    val msgMatcher: MessageMatcher,
    val repository: Repository,
    val startDate: Date,
    val endDate: Date
) {
    private val git: Git = Git(repository)
    private var gitPath: String? = null

    fun isCommitInBranch(commit: RevCommit, branchName: String): Boolean {
        val walk = RevWalk(this.repository)

        val targetCommit: RevCommit = walk.parseCommit(
            repository.resolve(commit.name)
        )

        return repository.allRefs.entries.find { (key, value) ->
            key.startsWith(Constants.R_HEADS) &&
                    walk.isMergedInto(targetCommit, walk.parseCommit(value.objectId)) &&
                    branchName == value.name
        } != null
    }

    fun getCommits(): Iterable<RevCommit> {
        return if (gitPath == null)
            git.log().all().call()
        else
            git.log()
                .add(git.repository.resolve(Constants.HEAD))
                .addPath(gitPath).call()
    }

    fun analyze(): List<IMessange> {

        val list =  getCommits().toList().filter { commit ->
            Date(commit.commitTime * 1000L).after(startDate) &&
                    Date(commit.commitTime * 1000L).before(endDate) &&
                    commit.parentCount > 0}

        val progressBar = ProgressBar("Repository scan", list.size.toLong())




        list.forEach {
                progressBar.step()
                it.fullMessage.split("\n".toRegex()).dropLastWhile { it.isEmpty() }
                    .filter { messange -> isFixMessage(messange) }
                    .forEach { messange -> msgMatcher.addNewMessage(messange) }
            }

        return msgMatcher.getResult(5)
    }

    fun isFixMessage(message: String): Boolean {
        return "fix" in message
    }
}