import { Application } from '@hotwired/stimulus';
import HostCheckController from './controllers/host_check_controller.js';

const app = Application.start();
app.register('host-check', HostCheckController);
