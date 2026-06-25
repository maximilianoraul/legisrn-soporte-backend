<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use App\Service\PythonApiService;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class HostCheckController extends AbstractController
{
    public function __construct(
        private PythonApiService $pythonApi,
    ) {
    }

    #[Route('/', name: 'host_check')]
    public function index(): Response
    {
        return $this->render('host_check/index.html.twig');
    }

    #[Route('/api/host-status', name: 'api_host_status')]
    public function hostStatus(Request $request): JsonResponse
    {
        $host = $request->query->get('host', '');
        if (empty($host)) {
            return new JsonResponse(['error' => 'Host requerido'], 400);
        }

        try {
            return new JsonResponse($this->pythonApi->getHostStatus($host));
        } catch (\Throwable $e) {
            return new JsonResponse(['error' => $e->getMessage()], 502);
        }
    }

    #[Route('/api/home-dirs', name: 'api_home_dirs')]
    public function homeDirs(Request $request): JsonResponse
    {
        $host = $request->query->get('host', '');
        if (empty($host)) {
            return new JsonResponse(['error' => 'Host requerido'], 400);
        }

        try {
            return new JsonResponse($this->pythonApi->getHomeDirs($host));
        } catch (\Throwable $e) {
            return new JsonResponse(['error' => $e->getMessage()], 502);
        }
    }

    #[Route('/api/logged-users', name: 'api_logged_users')]
    public function loggedUsers(Request $request): JsonResponse
    {
        $host = $request->query->get('host', '');
        if (empty($host)) {
            return new JsonResponse(['error' => 'Host requerido'], 400);
        }

        try {
            return new JsonResponse($this->pythonApi->getLoggedUsers($host));
        } catch (\Throwable $e) {
            return new JsonResponse(['error' => $e->getMessage()], 502);
        }
    }
}
