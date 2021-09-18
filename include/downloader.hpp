#pragma once

#include <set>
#include <thread>
#include <filesystem>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cassert>
extern "C" {
#include <unistd.h>

#include <fcntl.h>
}

#include <fmt/core.h>

namespace fs = std::filesystem;


#include "curl.hpp"
#include "utils.hpp"
#include "enums.hpp"
#include "mirror.hpp"
#include "download_target.hpp"
#include "target.hpp"
#include "zck.hpp"

class Downloader
{
public:
    Downloader();
    ~Downloader();

    void add(DownloadTarget *dl_target);

    /** Check the finished transfer
     * Evaluate CURL return code and status code of protocol if needed.
     * @param serious_error     Serious error is an error that isn't fatal,
     *                          but mirror that generate it should be penalized.
     *                          E.g.: Connection timeout - a mirror we are unable
     *                          to connect at is pretty useless for us, but
     *                          this could be only temporary state.
     *                          No fatal but also no good.
     * @param fatal_error       An error that cannot be recovered - e.g.
     *                          we cannot write to a socket, we cannot write
     *                          data to disk, bad function argument, ...
     */
    bool
    check_finished_transfer_status(CURLMsg *msg,
                                   Target *target);

    bool is_max_mirrors_unlimited();

    Mirror *select_suitable_mirror(Target *target);

    /* Select next target */
    bool select_next_target(Target **selected_target, std::string *selected_full_url);

    bool prepare_next_transfer(bool *candidate_found);

    bool prepare_next_transfers();

    /**
     * @brief Returns whether the download can be retried, using the same URL in case of base_url or full
     *        path, or using another mirror in case of using mirrors.
     *
     * @param complete_path_or_base_url determine type of download - mirrors or base_url/fullpath
     * @return gboolean Return TRUE when another chance to download is allowed.
     */
    bool can_retry_download(int num_of_tried_mirrors, const std::string &url);
    bool check_msgs(bool failfast);

    void download();

    bool failfast = false;
    CURLM *multi_handle;

    std::vector<Target *> m_targets;
    std::vector<Target *> m_running_transfers;

    int allowed_mirror_failures = 10;
    int max_mirrors_to_try = -1;
    int max_connection_per_host = -1;
    std::size_t max_parallel_connections = 5;

    std::map<std::string, std::vector<Mirror *> > mirror_map;

    // std::vector<DownloadTarget*> m_dl_targets;
};