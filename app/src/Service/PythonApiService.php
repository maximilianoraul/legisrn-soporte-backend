<?php

namespace App\Service;

use Symfony\Contracts\HttpClient\HttpClientInterface;

class PythonApiService
{
    public function __construct(
        private HttpClientInterface $httpClient,
        private string $apiBaseUrl,
    ) {
    }

    public function getHostStatus(string $host): array
    {
        return $this->callApi('/host-status', ['host' => $host]);
    }

    public function getHomeDirs(string $host): array
    {
        return $this->callApi('/home-dirs', ['host' => $host]);
    }

    public function getLoggedUsers(string $host): array
    {
        return $this->callApi('/logged-users', ['host' => $host]);
    }

    private function callApi(string $path, array $query = []): array
    {
        $url = $this->apiBaseUrl . $path . '?' . http_build_query($query);
        $response = $this->httpClient->request('GET', $url);
        return $response->toArray();
    }
}
